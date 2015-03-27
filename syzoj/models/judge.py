from syzoj import db
from random import randint
import time


class JudgeState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text)
    language = db.Column(db.String(20))
    result = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("submit", lazy='dynamic'))

    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    problem = db.relationship("Problem", backref=db.backref("submit", lazy='dynamic'))

    contest_id = db.Column(db.Integer, db.ForeignKey("contest.id"))
    contest = db.relationship("Contest", backref=db.backref("judges", lazy='dynamic'))

    submit_time = db.Column(db.Integer)  # googbye at 2038-1-19

    def __int__(self, code, language, user, problem, contest=None, submit_time=int(time.time())):
        self.code = code
        self.language = language
        self.user = user
        self.problem = problem
        self.submit_time = submit_time
        self.contest = contest

    def __repr__(self):
        print "<JudgeState %r>" % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()


class WaitingJudge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judge_id = db.Column(db.Integer, db.ForeignKey("judge_state.id"))
    judge = db.relationship("JudgeState", backref=db.backref("waiting_judge", lazy="dynamic"))

    def __init__(self, judge):
        self.judge = judge

    def __repr__(self):
        print "<WaitingJudge %r>" % self.judge_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
