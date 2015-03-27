from flask import Flask, jsonify, redirect, url_for, escape, abort, request, render_template
from syzoj import oj,db
from syzoj.models import get_problem_by_id,  JudgeState,WaitingJudge,get_judge_by_id
from syzoj.views.common import need_login, not_have_permission, show_error
from syzoj.views import get_user
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
        return redirect(url_for("judge_state",problem_id=problem.id))
    else:
        return render_template("submit.html",problem=problem,user=user,tab="judge")

@oj.route("/judge_state")
def judge_state():
    judges=JudgeState.query.order_by(db.desc(JudgeState.id)).all()
    return render_template("judge_state.html",user=get_user(),judges=judges,tab="judge")

@oj.route("/api/waiting_judge", methods=["GET"])
def get_judge_info():
    session_id = request.args.get('session_id')
    user = get_user(session_id=session_id)
    if not user.is_admin:
        abort(404)

    waiting_judges=WaitingJudge.query.all()
    if not len(waiting_judges):
        return jsonify({"have_task":0})
    waiting_judge=waiting_judges[0]
    judge=waiting_judge.judge
    #waiting_judge.delete()

    return jsonify({"have_task":1,
                    "judge_id":judge.id,
                    "code":judge.code,
                    "language":judge.language,
                    "testdate":judge.problem.testdata.filename})

@oj.route("/api/update_judge/<int:judge_id>", methods=["POST"])
def update_judge_info(judge_id):
    judge=get_judge_by_id(judge_id)
    if not judge:
        abort(404)
    print request.data
    #judge.result=request.data
    #judge.save()
    return jsonify({"status":1})
