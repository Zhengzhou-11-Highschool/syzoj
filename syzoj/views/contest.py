from urllib import urlencode
import time
from flask import render_template, url_for, request, abort, redirect
from syzoj import oj, db
from syzoj.models import Contest
from syzoj.controller import Tools, Paginate


@oj.route("/contest")
def contest_list():
    query = Contest.query.order_by(db.desc(Contest.id))

    def make_url(page, other):
        return url_for("contest_list") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=10)
    return render_template("contest_list.html", tool=Tools, sorter=sorter)


@oj.route("/contest/<int:contest_id>")
def contest(contest_id):
    contest = Contest.query.filter_by(id=contest_id).first()
    return render_template("contest.html", tool=Tools, contest=contest)


@oj.route("/contest/<int:contest_id>/<int:kth_problem>")
def contest_problem(contest_id, kth_problem):
    contest = Contest.query.filter_by(id=contest_id).first()
    if not contest:
        abort(404)

    now = time.time()
    if now < contest.start_time:
        abort(404)

    problem = contest.get_problems()[kth_problem]
    if now > contest.end_time:
        return redirect(url_for("problem", problem_id=problem.id))

    return render_template("contest_problem.html", tool=Tools, problem=problem, contest=contest)
