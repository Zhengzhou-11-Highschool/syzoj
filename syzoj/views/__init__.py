from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj
from syzoj.models import User,get_user
from .session import sign_up, login
from .problem import problem, problem_set
from .judge import submit_code,judge_state
from .user import user
from .discusstion import edit_article


@oj.route("/")
def index():
    return render_template("index.html", tab="index", user=get_user())


@oj.route("/error")
def error():
    info = request.args.get("info")
    next = request.args.get("next")
    return render_template("error_info.html", info=info, next=next, user=get_user())