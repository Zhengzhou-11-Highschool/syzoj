from .user import User, Session
from .problem import Problem, ProblemTag
from .judge import JudgeState,WaitingJudge
from .contest import Contest
from .article import Article, Comment
from .file import File


def get_problem_by_id(problem_id):
    problems = Problem.query.filter_by(id=problem_id)
    if problems.count():
        return problems.first()
    else:
        return None