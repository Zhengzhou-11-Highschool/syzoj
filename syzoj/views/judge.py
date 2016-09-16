from urllib import urlencode
import json

from flask import jsonify, redirect, url_for, abort, request, render_template

from syzoj import oj, db
from syzoj.controller import Tools
from syzoj.models import JudgeState, WaitingJudge, Problem, User, Contest
from syzoj.controller import Paginate
from .common import need_login, not_have_permission, show_error


@oj.route("/submit/<int:problem_id>", methods=["GET", "POST"])
def submit_code(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)

    if request.method == "POST":
        code = request.form.get("code")
 #       language = "C++"  # Qinding is not good
        language = request.form.get("language")
        if not code or len(code) <= 0 or len(code) >= 1024 * 100:
            return show_error("Please check out your code length.The code should less than 100kb.",
                              url_for("submit_code", problem_id=problem.id))

        judge = JudgeState(code=code, user=user, language=language, problem=problem)

        contest_id = request.args.get("contest_id")
        if contest_id:
            contest = Contest.query.filter_by(id=contest_id).first()
            if contest and contest.is_running():
                judge.type = 1
                judge.type_info = contest_id
            else:
                return show_error("Sorry.The contest has been ended.", next=url_for("contest", contest_id=contest.id))
        else:
            if not problem.is_allowed_use(user):
                return show_error("Sorry.You don't have permission.", next=url_for("index"))
            if not problem.is_public:
                judge.type = 2

        judge.save()
        waiting = WaitingJudge(judge)
        waiting.save()
        return redirect(url_for("judge_detail", judge_id=judge.id))
    else:
        return render_template("submit.html", tool=Tools, problem=problem, tab="judge")


@oj.route("/judge_state")
def judge_state():
    query = JudgeState.query.order_by(db.desc(JudgeState.id))
    nickname = request.args.get("submitter")
    problem_id = request.args.get("problem_id")
    if request.args.get("submitter"):
        submitter = User.query.filter_by(nickname=nickname).first()
        if submitter:
            submitter_id = submitter.id
        else:
            submitter_id = 0
        query = query.filter_by(user_id=submitter_id)
    if request.args.get("problem_id"):
        query = query.filter_by(problem_id=int(problem_id))

    def make_url(page, other):
        other["page"] = page
        return url_for("judge_state") + "?" + urlencode(other)

    if not nickname:
        nickname = ""
    if not problem_id:
        problem_id = ""
    sorter = Paginate(query, make_url=make_url, other={"submitter": nickname, "problem_id": problem_id},
                      cur_page=request.args.get("page"), edge_display_num=3, per_page=10)

    return render_template("judge_state.html", user=User.get_cur_user(), judges=sorter.get(), tab="judge",
                           submitter=nickname, problem_id=problem_id, sorter=sorter, encode=urlencode, tool=Tools)


@oj.route("/api/waiting_judge", methods=["GET"])
def get_judge_info():
    session_id = request.args.get('session_id')
    if oj.config["JUDGE_TOKEN"] != session_id:
        abort(404)

    waiting_judge = WaitingJudge.query.first()
    if not waiting_judge:
        return jsonify({"have_task": 0})
    judge = waiting_judge.judge
    waiting_judge.delete()

    return jsonify({"have_task": 1,
                    "judge_id": judge.id,
                    "code": judge.code,
                    "language": judge.language,
                    "testdata": judge.problem.testdata.md5,
                    "time_limit": judge.problem.time_limit,
                    "memory_limit": judge.problem.memory_limit})


@oj.route("/api/update_judge/<int:judge_id>", methods=["POST"])
def update_judge_info(judge_id):
    token = request.args.get('session_id')
    if oj.config["JUDGE_TOKEN"] != token:
        abort(404)

    judge = JudgeState.query.filter_by(id=judge_id).first()
    if not judge:
        abort(404)

    judge.update_result(json.loads(request.form["result"]))
    judge.update_related_info()
    judge.save()

    return jsonify({"return": 0})


@oj.route("/judge_detail/<int:judge_id>")
def judge_detail(judge_id):
    judge = JudgeState.query.filter_by(id=judge_id).first()
    if not judge:
        abort(404)

    return render_template("judge_detail.html", judge=judge, user=User.get_cur_user(), tab="judge", tool=Tools)
