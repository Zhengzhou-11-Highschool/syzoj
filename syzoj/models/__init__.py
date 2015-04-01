from flask import request
from .user import User, Session
from .problem import Problem, ProblemTag
from .judge import JudgeState, WaitingJudge
from .contest import Contest
from .article import Article, Comment
from .file import File


def get_problem_by_id(problem_id):
    return Problem.query.filter_by(id=problem_id).first()


def get_user(username=None, session_id=None):
    if username == None:
        if session_id == None:
            session_id = request.cookies.get('session_id')
        sessions = Session.query.filter_by(id=session_id).all()
        for s in sessions:
            if s.is_valid():
                return s.user
    else:
        user = User.query.filter_by(username=username).first()
        return user


def get_judge_by_id(judge_id):
    judge = JudgeState.query.filter_by(id=judge_id).first()
    return judge