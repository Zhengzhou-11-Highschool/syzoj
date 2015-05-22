from urllib import urlencode

from flask import jsonify, redirect, url_for, abort, request, render_template

from syzoj import oj
from syzoj.models import User, Problem, File
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error

@oj.route("/problem")
def problem_set():
    query = Problem.query

    def make_url(page, other):
        return url_for("problem_set") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=50, per_page=50)
    return render_template("problem_set.html", tool=Tools, tab="problem_set", sorter=sorter)


@oj.route("/problem/<int:problem_id>")
def problem(problem_id):
    user = User.get_cur_user()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)

    if problem.is_allowed_use(user) == False:
        return not_have_permission()

    return render_template("problem.html", tool=Tools, tab="problem_set", problem=problem)


@oj.route("/problem/<int:problem_id>/edit", methods=["GET", "POST"])
def edit_problem(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()
    if problem and problem.is_allowed_edit(user) == False:
        return not_have_permission()

    if request.method == "POST":
        if request.form.get("title") == "" or request.form.get("description") == "":
            return show_error("Please input title and problem description",
                              url_for("edit_problem", problem_id=problem_id))

        if not problem:
            problem = Problem(user=user, title=request.form.get("title"))

        problem.title = request.form.get("title")
        problem.description = request.form.get("description")
        problem.input_format = request.form.get("input_format")
        problem.output_format = request.form.get("output_format")
        problem.example = request.form.get("example")
        problem.limit_and_hint = request.form.get("limit_and_hint")

        problem.save()

        return redirect(url_for("problem", problem_id=problem.id))
    else:
        return render_template("edit_problem.html", tool=Tools, problem=problem)


@oj.route("/problem/<int:problem_id>/upload", methods=["GET", "POST"])
def upload_testdata(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(problem_id=problem_id).first()
    if not problem:
        abort(404)
    if problem.is_allowed_edit(user) == False:
        return not_have_permission()
    if request.method == "POST":
        file = request.files.get("testdata")
        # Todo:suit new File'interface
        if file:
            testdata = File(file)
            testdata.filename += ".zip"
            testdata.save()
            problem.testdata = testdata
        if request.form.get("time_limit"):
            problem.time_limit = int(request.form.get("time_limit"))
        if request.form.get("memory_limit"):
            problem.memory_limit = int(request.form.get("memory_limit"))
        problem.save()
        return redirect(url_for("upload_testdata", tool=Tools, problem_id=problem_id))
    else:
        return render_template("upload_testdata.html", problem=problem, user=user)


# TODO:Maybe need add the metho of toggle is_public attr to Problem
@oj.route("/api/problem/<int:problem_id>/public", methods=["POST", "DELETE"])
def change_public_attr(problem_id):
    session_id = request.args.get('session_id')
    user = User.get_cur_user(session_id=session_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    if problem and user and user.is_admin:
        if request.method == "POST":
            problem.is_public = True
        elif request.method == "DELETE":
            problem.is_public = False
        problem.save()
    else:
        abort(404)
    return jsonify({"status": 0})
