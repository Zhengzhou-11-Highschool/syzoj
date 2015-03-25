from flask import Flask, jsonify, redirect, url_for, escape, request, render_template
from syzoj import oj
from syzoj.models import User
from syzoj.api import get_user


@oj.route("/login")
def login():
    return render_template("login.html", user=get_user())


@oj.route("/sign_up")
def sign_up():
    return render_template("sign_up.html", user=get_user())
