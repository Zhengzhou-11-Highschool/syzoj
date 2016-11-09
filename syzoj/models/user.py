from flask import request
from syzoj import db
from .problem import Problem
import urllib, hashlib
from random import randint
import time


class Session(db.Model):
    id = db.Column(db.String(120), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("sessions", lazy='dynamic'))

    login_time = db.Column(db.Integer)  # googbye at 2038-1-19
    expiration_time = db.Column(db.Integer)

    def __init__(self, user, login_time=None, valid_time=3600 * 24 * 7):
        if not login_time:
            login_time = int(time.time())
        self.id = str(randint(1, int(1e50)))
        self.user = user
        self.login_time = login_time
        self.expiration_time = login_time + valid_time

    def __repr__(self):
        print "<Session_id %r User_id %r" % (self.id, self.user_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_valid(self, now=None):
        # print "now:%r expiration_tim:%r" % (now,self.expiration_time)
        if not now:
            now = int(time.time())
        if now < self.expiration_time:
            return True
        else:
            self.delete()
            return False


class UserPrivilege(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, index = True)
    privilege_type = db.Column(db.Integer)
    '''
    1 administator
    2 problem manager
    3 view all problem
    4 contest manager
    5 contest builder
    6 article manager
    7 user manager
    8 data download
    '''
    
    def __init__(self, user_id, privilege_type):
        self.user_id = user_id
        self.privilege_type = privilege_type
        
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    nickname = db.Column(db.String(80), index=True)
    nameplate = db.Column(db.Text)
    information = db.Column(db.Text)

    ac_num = db.Column(db.Integer, index=True)
    submit_num = db.Column(db.Integer)

    is_admin = db.Column(db.Boolean)

    def get_gravatar_url(self, size=40):
        url = "http://cn.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        url += urllib.urlencode({'d': 'mm', 's': str(size)})
        return url

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

        self.nickname = username
        self.is_admin = False
        self.ac_num = 0
        self.submit_num = 0

    def __repr__(self):
        return "<User:%r password:%r email:%r>" % (self.username, self.password, self.email)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def have_privilege(self, privilege_type):
        for privilege in UserPrivilege.query.filter_by(user_id = self.id).all():
            if privilege.privilege_type == privilege_type or privilege.privilege_type == 1:
                return True
        return False

    def is_allowed_edit(self, user):
        if not user:
            return False
        if self.id == user.id or user.have_privilege(7):
            return True
        return False

    def get_submitted_problems(self):
        submitted_problems = dict()
        for ac_info in UserAcProblem.query.filter_by(user_id = self.id).all():
            submitted_problems[ac_info.problem_id] = [ac_info.is_accepted, ac_info.judge_id]
        return submitted_problems

    def refresh_submit_info(self):
        cnt = 0
        for ac_info in UserAcProblem.query.filter_by(user_id = self.id).all():
            if ac_info.is_accepted:
                cnt += 1
        self.ac_num = cnt

    @staticmethod
    def get_cur_user(session_id=None):
        if not session_id:
            session_id = request.cookies.get('session_id')

        sessions = Session.query.filter_by(id=session_id).all()
        for s in sessions:
            if s.is_valid():
                return s.user

        return None

    @staticmethod
    def find_user(nickname=None, id=None):
        if id:
            return User.query.filter_by(id=id).first()

        if nickname:
            return User.query.filter_by(nickname=nickname).first()

        return None
        
    def give_privilege(self, privilege_type):
        for privilege in UserPrivilege.query.filter_by(user_id = self.id).all():
            if privilege.privilege_type == privilege_type:
                return False # User already had privilege
        new_privilege = UserPrivilege(user_id = self.id, privilege_type = privilege_type)
        new_privilege.save()
        return True
        
    def del_privilege(self, privilege_type):
        for privilege in UserPrivilege.query.filter_by(user_id = self.id).all():
            if privilege.privilege_type == privilege_type:
                privilege.delete()
                return True
        return False # User doesnt have privilege

class UserAcProblem(db.Model):
    __tablename__ = 'UserAcProblem'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, index = True)
    problem_id = db.Column(db.Integer)
    is_accepted = db.Column(db.BOOLEAN)
    judge_id = db.Column(db.Integer)

    def __init__(self, user_id, problem_id, judge_id):
        self.user_id = user_id
        self.problem_id = problem_id
        self.is_accepted = False
        self.judge_id = judge_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

        

