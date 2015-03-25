from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj
from syzoj.models import User
from syzoj.api import get_user


@oj.route("/problem")
def problem_set():
    return render_template("problem_set.html", tab="problem_set", user=get_user())


@oj.route("/problem/<int:problem_id>")
def problem(problem_id):
    return render_template("problem.html", tab="problem_set", user=get_user())

