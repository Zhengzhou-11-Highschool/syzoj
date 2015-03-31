from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj,db
from syzoj.views.common import need_login, not_have_permission, show_error, Paginate
from syzoj.models import User,Session,get_user
from urllib import urlencode

@oj.route("/user/<int:user_id>")
def user(user_id):
    user=User.query.filter_by(id=user_id).first()
    if not user:
        return show_error("Can't find user",next=url_for("index"))
    ac_problems=set()
    user.submit_num=user.submit.count()
    for judge in user.submit.all():
        if judge.is_allowed_see_result(None) and judge.status=="Accepted":
            ac_problems.add(judge.problem_id)
    user.ac_num=len(ac_problems)
    user.save()

    return render_template("user.html",user=get_user(),show_user=user,ac_problems=ac_problems)

@oj.route("/ranklist")
def ranklist():
    query=User.query.order_by(db.desc(User.ac_num))
    sorter=Paginate(query,cur_page=request.args.get("page"),edge_display_num=3,per_page=50)
    return render_template("ranklist.html",user=get_user(),users=sorter.get(),sorter=sorter,tab="ranklist",
                           encode=urlencode)