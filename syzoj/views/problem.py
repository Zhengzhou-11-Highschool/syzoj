from flask import Flask, jsonify, redirect, url_for, escape, abort, request, render_template
from syzoj import oj
from syzoj.models import User, Problem, get_problem_by_id, File, JudgeState,WaitingJudge
from syzoj.api import get_user
from syzoj.views.common import need_login, not_have_permission, show_error
from random import randint
import os


@oj.route("/problem")
def problem_set():
    problems = Problem.query.all()
    return render_template("problem_set.html", tab="problem_set", user=get_user(), problems=problems)


@oj.route("/problem/<int:problem_id>")
def problem(problem_id):
    user = get_user()
    problem = get_problem_by_id(problem_id)
    if not problem:
        abort(404)
    if problem.is_allowed_use(user) == False:
        return not_have_permission()
    return render_template("problem.html", tab="problem_set", user=get_user(), problem=problem)


@oj.route("/problem/<int:problem_id>/edit", methods=["GET", "POST"])
def edit_problem(problem_id):
    user = get_user()
    if not user:
        return need_login()

    problem = get_problem_by_id(problem_id)
    if problem and problem.is_allowed_edit(user) == False:
        return not_have_permission()
    print request.method
    if request.method == "POST":
        if request.form.get("title") == "" or request.form.get("description") == "":
            return show_error("Please input title and problem description",
                              url_for("edit_problem", problem_id=problem_id))

        if not problem:
            problem = Problem(user=user,
                              title=request.form.get("title")
                              )

        problem.title = request.form.get("title")
        problem.description = request.form.get("description")
        problem.input_format = request.form.get("input_format")
        problem.output_format = request.form.get("output_format")
        problem.example = request.form.get("example")
        problem.limit_and_hint = request.form.get("limit_and_hint")

        problem.save()

        return redirect(url_for("problem", problem_id=problem.id))
    else:
        return render_template("edit_problem.html", problem=problem, user=user)


@oj.route("/problem/<int:problem_id>/upload", methods=["GET", "POST"])
def upload_testdata(problem_id):
    user = get_user()
    if not user:
        return need_login()

    problem = get_problem_by_id(problem_id)
    if not problem:
        abort(404)
    if problem.is_allowed_edit(user) == False:
        return not_have_permission()
    if request.method == "POST":
        file = request.files.get("testdata")
        if file:
            testdata = File(str(randint(1, int(1e50))) + ".zip")
            file.save(os.path.join(oj.config["UPLOAD_FOLDER"], testdata.filename))
            testdata.save()
            problem.testdata =testdata
        if request.form.get("time_limit"):
            problem.time_limit=int(request.form.get("time_limit"))
        if request.form.get("memory_limit"):
            problem.memory_limit=int(request.form.get("memory_limit"))
        problem.save()
        return redirect(url_for("upload_testdata", problem_id=problem_id))
    else:
        return render_template("upload_testdata.html", problem=problem,user=user)

