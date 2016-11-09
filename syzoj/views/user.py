from flask import redirect, url_for, request, render_template

from syzoj import oj, db
from syzoj.models import User, Article
from syzoj.controller import Paginate, Tools, Checker
from .common import not_have_permission, show_error

@oj.route("/user/<int:user_id>")
def user(user_id):
    user = User.find_user(id=user_id)
    if not user:
        return show_error("Can't find user", next=url_for("index"))

    user.refresh_submit_info()
    user.save()

    articles = Article.query.filter_by(user_id = user.id).order_by(Article.public_time.desc()).all()
    articles_num = len(articles)

    return render_template("user.html", tool=Tools, shown_user=user,
                            articles_num = articles_num, articles = articles)

@oj.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    edited_user = User.find_user(id=user_id)
    if not edited_user:
        return show_error("Can't find user", next=url_for("index"))

    user = User.get_cur_user()
    if not edited_user.is_allowed_edit(user):
        return not_have_permission()

    if request.method == "POST":
        email = request.form.get("email")
        information = request.form.get("information")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        if user.have_privilege(1):
            if request.form.get("prb_mng"):
                edited_user.give_privilege(2)
            else:
                edited_user.del_privilege(2)
            if request.form.get("vwa_prb"):
                edited_user.give_privilege(3)
            else:
                edited_user.del_privilege(3)
            if request.form.get("cts_mng"):
                edited_user.give_privilege(4)
            else:
                edited_user.del_privilege(4)
            if request.form.get("cts_bld"):
                edited_user.give_privilege(5)
            else:
                edited_user.del_privilege(5)
            if request.form.get("atc_mng"):
                edited_user.give_privilege(6)
            else:
                edited_user.del_privilege(6)
            if request.form.get("usr_mng"):
                edited_user.give_privilege(7)
            else:
                edited_user.del_privilege(7)
            if request.form.get("dat_dld"):
                edited_user.give_privilege(8)
            else:
                edited_user.del_privilege(8)

        status = 1
        if not Checker.is_valid_email(email):
            status = 3001

        if information == "":
            information = None

        if old_password:
            if edited_user.password != old_password:
                status = 3002
            else:
                if Checker.is_valid_password(new_password):
                    edited_user.password = new_password
                else:
                    status = 3003

        if status == 1:
            edited_user.email = email
            edited_user.information = information
            edited_user.save()

        return render_template("edit_user.html", tool=Tools, edited_user=edited_user, status=status)
    else:
        return render_template("edit_user.html", tool=Tools, edited_user=edited_user)


@oj.route("/ranklist")
def ranklist():
    query = User.query.order_by(db.desc(User.ac_num))

    def make_url(page, other):
        return url_for("ranklist") + "?" + Tools.url_encode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=50)

    return render_template("ranklist.html", tool=Tools, sorter=sorter, tab="ranklist")


@oj.route("/find_user")
def find_user():
    nickname = request.args.get("nickname")
    user = User.find_user(nickname=nickname)
    if not user:
        return show_error("Can't find " + nickname, url_for("ranklist"))

    return redirect(url_for("user", user_id=user.id))
