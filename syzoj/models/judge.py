from syzoj import db
from random import randint
import json
import time


class JudgeState(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    code = db.Column(db.Text)
    language = db.Column(db.String(20))

    status = db.Column(db.String(50))
    result = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("submit", lazy='dynamic'))

    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"), index=True)
    problem = db.relationship("Problem", backref=db.backref("submit", lazy='dynamic'))

    contest_id = db.Column(db.Integer, db.ForeignKey("contest.id"), index=True)
    contest = db.relationship("Contest", backref=db.backref("judges", lazy='dynamic'))

    submit_time = db.Column(db.Integer)  # googbye at 2038-1-19

    def __init__(self, code, language, user, problem, contest=None, submit_time=None):
        if not submit_time:
            submit_time = int(time.time())
        self.code = code
        self.language = language
        self.user = user
        self.problem = problem
        self.submit_time = submit_time
        self.contest = contest

        self.status = "Waiting"
        self.result = '{"status": "Waiting", "total_time": 0, "total_memory": 0, "score":0, "case": 0}'

    def __repr__(self):
        print "<JudgeState %r>" % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def is_allowed_see_result(self, user):
        if self.problem.is_allowed_edit(user):
            return True
        if self.contest and self.contest.is_running():
            return False
        return self.problem.is_public

    def is_allowed_see_code(self, user):
        if user:
            if user.is_admin or self.user.id == user.id:
                return True
        return self.is_allowed_see_result(user)

    def result_dict(self):
        return json.loads(self.result)

    def pretty_submit_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.submit_time))


class WaitingJudge(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
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
