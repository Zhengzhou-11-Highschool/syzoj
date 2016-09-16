from flask import jsonify, request, render_template

from syzoj import oj
from syzoj.models import User, Session
from syzoj.controller import Tools
from syzoj import controller

@oj.route("/login")
def login():
    return render_template("login.html", tool=Tools)


@oj.route("/sign_up")
def sign_up():
    return render_template("sign_up.html", tool=Tools)


@oj.route("/api/sign_up", methods=["POST"])
def api_sign_up():
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    error_code = controller.register(username, password, email)
    return jsonify({"error_code": error_code})


@oj.route("/api/login", methods=["POST"])
def api_login():
    error_code = 1
    session_id = "???"
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user:
        error_code = 1001
    elif user.password != password:
        error_code = 1002
    else:
        session = Session(user)
        session.save()
        session_id = session.id
    return jsonify({"error_code": error_code, "session_id": session_id})


@oj.route("/api/logout", methods=["POST"])
def api_logout():
    session_id = request.args.get('session_id')
    user = User.get_cur_user(session_id=session_id)
    sessions = user.sessions.all()
    for s in sessions:
        s.delete()
    return jsonify({"status": "1"})