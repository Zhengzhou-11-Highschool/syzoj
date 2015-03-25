from syzoj import db
from random import randint
import time

problems_table = db.Table('contest_problems',
                          db.Column('problem_id', db.Integer, db.ForeignKey('problem.id')),
                          db.Column('contest_id', db.Integer, db.ForeignKey('contest.id'))
                          )
players_table = db.Table('contest_players',
                         db.Column('player_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('contest_id', db.Integer, db.ForeignKey('contest.id'))
                         )


class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    start_time = db.Column(db.Integer)  # googbye at 2038-1-19
    end_time = db.Column(db.Integer)

    holder_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    holder = db.relationship("User", backref=db.backref("hold_contests", lazy='dynamic'))

    problems = db.relationship('Problem', secondary=problems_table, backref=db.backref('contests', lazy='dynamic'))
    information = db.Column(db.Text)

    player = db.relationship('User', secondary=players_table, backref=db.backref('contests', lazy='dynamic'))

    def __init__(self, title, start_time, end_time, holder):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.holder = holder

    def __repr__(self):
        print "<Contest %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()