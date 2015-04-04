from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj, db
from syzoj.views.common import need_login, not_have_permission, show_error, Paginate
from syzoj.models import User, Session, get_user
from syzoj.views.session import is_valid_email, is_valid_password
from urllib import urlencode


@oj.route("/user/<int:user_id>")
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return show_error("Can't find user", next=url_for("index"))
    ac_problems = set()
    user.submit_num = user.submit.count()
    for judge in user.submit.all():
        if judge.is_allowed_see_result(None) and judge.status == "Accepted":
            ac_problems.add(judge.problem_id)
    user.ac_num = len(ac_problems)
    user.save()

    return render_template("user.html", user=get_user(), show_user=user, ac_problems=ac_problems)


@oj.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    edited_user = User.query.filter_by(id=user_id).first()
    if not edited_user:
        return show_error("Can't find user", next=url_for("index"))

    user = get_user()
    if not edited_user.is_allowed_edit(user):
        return not_have_permission()

    if request.method == "POST":
        # nickname=request.form.get("nickname")
        status = 1
        email = request.form.get("email")
        information = request.form.get("information")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        if not is_valid_email(email):
            status = 3001

        if is_valid_password(old_password):
            if edited_user.password != old_password:
                status = 3002
            else:
                if is_valid_password(new_password):
                    edited_user.password = new_password
                else:
                    status = 3003

        if information == "":
            information = None
        if status == 1:
            edited_user.email = email
            edited_user.information = information
            edited_user.save()

        return render_template("edit_user.html", user=user, edited_user=edited_user, status=status)
    else:
        return render_template("edit_user.html", user=user, edited_user=edited_user)


@oj.route("/ranklist")
def ranklist():
    query = User.query.order_by(db.desc(User.ac_num))

    def make_url(page, other):
        return url_for("ranklist") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=50)
    return render_template("ranklist.html", user=get_user(), users=sorter.get(), sorter=sorter, tab="ranklist")


@oj.route("/find_user")
def find_user():
    nickname = request.args.get("nickname")
    if not nickname:
        return show_error("Please input user's nickname.", url_for("ranklist"))
    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        return show_error("Can't find " + nickname, url_for("ranklist"))
    return redirect(url_for("user", user_id=user.id))