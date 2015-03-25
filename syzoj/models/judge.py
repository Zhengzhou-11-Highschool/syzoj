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

    submit_time = db.Column(db.Integer)  # googbye at 2038-1-19

    def __int__(self, code, language, user, problem, submit_time=int(time.time())):
        self.code = code
        self.language = language
        self.user = user
        self.problem = problem
        self.submit_time = submit_time

    def __repr__(self):
        print "<JudgeState %r>" % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()
