from syzoj import oj
from flask import Flask, jsonify, redirect, url_for, request, render_template
from syzoj.models import User,Session
import json
import os, re


def get_user(username=None, session_id=None):
    if username == None:
        if session_id == None:
            session_id = request.cookies.get('session_id')
        sessions=Session.query.filter_by(id=session_id).all()
        for s in sessions:
            if s.is_valid():
                return s.user
    else:
        user = User.query.filter_by(username=username)
        if user.count():
            return user.first()
    return None

def is_valid_username(username):
    if len(username) < 3 or len(username) > 16:
        return False
    checker = re.compile("[A-Za-z0-9_]")
    if not checker.match(username):
        return False
    return True


def is_valid_email(email):
    if len(email) < 3 or len(email) > 50:
        return False
    checker = re.compile("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$")
    if not checker.match(email):
        return False
    return True


def is_valid_password(password):
    syzoj2_xxx = "59cb65ba6f9ad18de0dcd12d5ae11bd2"
    if len(password) != len(syzoj2_xxx):
        return False
    if password == syzoj2_xxx:
        return False
    return True


def check_is_valid_user(user):
    if not is_valid_username(user.username):
        return 2005
    elif not is_valid_email(user.email):
        return 2006
    elif not is_valid_password(user.password):
        return 2007
    else:
        return 1


@oj.route("/api/sign_up", methods=["POST"])
def api_sign_up():
    error_code = 1
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    if get_user(username=username):
        error_code = 2008
    else:
        user = User(username=username, password=password, email=email)
        error_code = check_is_valid_user(user)
        if error_code == 1:
            user.save()
            print user
    return jsonify({"error_code": error_code})


@oj.route("/api/login", methods=["POST"])
def api_login():
    error_code = 1
    session_id = "???"
    username = request.args.get('username')
    password = request.args.get('password')
    user = get_user(username=username)
    if not user:
        error_code = 1001
    elif user.password != password:
        error_code = 1002
    else:
        session=Session(user)
        session.save()
        session_id=session.id
    return jsonify({"error_code": error_code, "session_id": session.id})


@oj.route("/api/logout", methods=["POST"])
def api_logout():
    session_id = request.args.get('session_id')
    user = get_user(session_id=session_id)
    sessions=user.sessions.all()
    for s in sessions:
        s.delete()
    return jsonify({"status": "1"})