from syzoj import db
from random import randint
import time


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    session_id = db.Column(db.String(120))

    nickname = db.Column(db.String(80))
    nameplate = db.Column(db.Text)
    information = db.Column(db.Text)

    is_admin = db.Column(db.Boolean)

    def make_session_id(self):
        self.session_id = str(randint(1, int(1e50)))

    def __init__(self, username, passowrd, email):
        self.username = username
        self.password = password
        self.email = email

        self.nickname = username
        self.is_admin = False
        self.make_session_id()

    def __repr__(self):
        return "<User:%r password:%r email:%r>" % (self.username, self.password, self.email)

    def save(self):
        db.session.add(self)
        db.session.commit()