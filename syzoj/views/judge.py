from flask import Flask, jsonify, redirect, url_for, escape, abort, request, render_template
from syzoj import oj,db
from syzoj.models import get_problem_by_id,  JudgeState,WaitingJudge,get_judge_by_id, get_user
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
        return redirect(url_for("judge_detail",judge_id=judge.id))
    else:
        return render_template("submit.html",problem=problem,user=user,tab="judge")

@oj.route("/judge_state")
def judge_state():
    judges=JudgeState.query.order_by(db.desc(JudgeState.id)).all()
    return render_template("judge_state.html",user=get_user(),judges=judges,tab="judge")

@oj.route("/api/waiting_judge", methods=["GET"])
def get_judge_info():
    session_id = request.args.get('session_id')
    if oj.config["JUDGE_TOKEN"]!=session_id:
        abort(404)

    waiting_judge=WaitingJudge.query.first()
    if not waiting_judge:
        return jsonify({"have_task":0})
    judge=waiting_judge.judge
    waiting_judge.delete()

    return jsonify({"have_task":1,
                    "judge_id":judge.id,
                    "code":judge.code,
                    "language":judge.language,
                    "testdata":judge.problem.testdata.filename,
                    "time_limit":judge.problem.time_limit,
                    "memory_limit":judge.problem.memory_limit})

@oj.route("/api/update_judge/<int:judge_id>", methods=["POST"])
def update_judge_info(judge_id):
    judge=get_judge_by_id(judge_id)
    session_id = request.args.get('session_id')
    if oj.config["JUDGE_TOKEN"]!=session_id:
        abort(404)

    print request.form["result"]
    judge.result=request.form["result"]
    judge.save()

    if judge.is_allowed_see_result(None):
        print "allow_to_see"
        judge.problem.ac_num+=1
        judge.problem.submit_num+=1
        judge.user.ac_num+=1
        judge.user.submit_num+=1
        judge.problem.save()
        judge.user.save()
    return jsonify({"status":1})

@oj.route("/judge_detail/<int:judge_id>")
def judge_detail(judge_id):
    judge=get_judge_by_id(judge_id)
    if not judge:
        abort(404)
    return render_template("judge_detail.html",judge=judge,user=get_user(),tostr=str)