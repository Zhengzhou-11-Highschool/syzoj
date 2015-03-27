from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj
from syzoj.models import User
from syzoj.api import get_user
from .problem import problem, problem_set
from .session import sign_up, login
from .judge import submit_code,judge_state


@oj.route("/")
def index():
    return render_template("index.html", tab="index", user=get_user())


@oj.route("/error")
def error():
    info = request.args.get("info")
    next = request.args.get("next")
    return render_template("error_info.html", info=info, next=next, user=get_user())