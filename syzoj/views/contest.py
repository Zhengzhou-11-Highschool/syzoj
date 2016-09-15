# -*- coding: utf-8 -*-

from urllib import urlencode
import time
from flask import render_template, url_for, request, abort, redirect
from syzoj import oj, db
from syzoj.models import Contest, User, JudgeState
from syzoj.controller import Tools, Paginate
from .common import need_login, not_have_permission


@oj.route("/contest")
def contest_list():
    query = Contest.query.order_by(db.desc(Contest.start_time))

    def make_url(page, other):
        return url_for("contest_list") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=10)
    return render_template("contest_list.html", tool=Tools, sorter=sorter, now=time.time())


@oj.route("/contest/<int:contest_id>")
def contest(contest_id):
    contest = Contest.query.filter_by(id=contest_id).first()
    user = User.get_cur_user()
    player = None
    info = {}
    if user: player = contest.players.filter_by(user_id = user.id).first()
    if player:
        details = player.get_score_details()
        for key, val in details.iteritems():
            if isinstance(val, dict):
                pid = int(key)
                jid = int(val["judge_id"])
                status = JudgeState.query.filter_by(id = jid).first().status
                url = url_for("judge_detail", judge_id = jid)
                if contest.is_running():
                    info[pid] = u"<a href = '%s'>已提交</a>" % (url)
                else:
                    info[pid] = "<a href = '%s'>%s</a>" % (url, status)
        
    return render_template("contest.html", tool=Tools, contest=contest, info = info)


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


@oj.route("/contest/<int:contest_id>/ranklist")
def contest_ranklist(contest_id):
    user = User.get_cur_user()
    contest = Contest.query.filter_by(id=contest_id).first()
    if not contest:
        abort(404)
    now = time.time()
    if contest.is_allowed_edit(user) or now > contest.end_time:
        return render_template("contest_ranklist.html", tool=Tools, contest=contest)
    else:
        return not_have_permission()


@oj.route("/contest/<int:contest_id>/edit", methods=["GET", "POST"])
def edit_contest(contest_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    contest = Contest.query.filter_by(id=contest_id).first()
    if contest and not contest.is_allowed_edit(user):
        return not_have_permission()

    if request.method == "POST":
        if not contest:
            contest = Contest(title=request.form.get("title"),
                              start_time=request.form.get("start_time"),
                              end_time=request.form.get("end_time"),
                              holder=user)

        contest.title = request.form.get("title")
        contest.start_time = request.form.get("start_time")
        contest.end_time = request.form.get("end_time")
        contest.information = request.form.get("information")

        try:
            problems_list = [int(pid) for pid in request.form.get("problems").split(",")]
        except:
            problems_list = []
        contest.set_problems(problems_list)

        contest.save()

        return redirect(url_for("contest", contest_id=contest.id))
    else:
        return render_template("edit_contest.html", tool=Tools, contest=contest)
