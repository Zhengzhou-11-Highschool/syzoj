from flask import Flask, jsonify, redirect, url_for, escape, abort, request, render_template
from syzoj import oj,db
from syzoj.models import User, Problem, get_problem_by_id, File, JudgeState,WaitingJudge
from syzoj.api import get_user
from syzoj.views.common import need_login, not_have_permission, show_error
from random import randint
import os

@oj.route("/submit/<int:problem_id>",methods=["GET", "POST"])
def submit_code(problem_id):
    user = get_user()
    if not user:
        return need_login()

    problem = get_problem_by_id(problem_id)
    if not problem:
        abort(404)

    if problem.is_allowed_use(user) == False:
        return not_have_permission()

    if request.method == "POST":
        code=request.form.get("code")
        if not code or len(code)<=0 or len(code)>=1024*100:
            return show_error("Please check out your code length.The code should less than 100kb.",
                              url_for("submit_code",problem_id=problem.id))
        language="C++" #...
        judge=JudgeState(code=code,user=user,language=language,problem=problem)
        judge.save()
        waiting=WaitingJudge(judge)
        waiting.save()
        return redirect(url_for("problem",problem_id=problem.id)) #temporarily
    else:
        return render_template("submit.html",problem=problem,user=user,tab="judge")

@oj.route("/judge_state")
def judge_state():
    judges=JudgeState.query.order_by(db.desc(JudgeState.id)).all()
    return render_template("judge_state.html",user=get_user(),judges=judges,tab="judge")