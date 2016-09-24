from syzoj import db
from syzoj.models.contest import Contest
from syzoj.models.user import UserAcProblem
import json
import time


class JudgeState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text)
    language = db.Column(db.String(20))

    status = db.Column(db.String(50), index=True)
    score = db.Column(db.Integer, index=True)
    result = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("submit", lazy='dynamic'))

    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"), index=True)
    problem = db.relationship("Problem", backref=db.backref("submit", lazy='dynamic'))

    submit_time = db.Column(db.Integer)  # googbye at 2038-1-19

    # "type" indicate it's contest's submission(type = 0) or normal submission(type = 1)
    # type=2: this is a test submission
    # if it's contest's submission (type = 1), the type_info is contest_id
    # use this way represent because it's easy to expand
    type = db.Column(db.Integer)
    type_info = db.Column(db.Integer)

    def __init__(self, code, language, user, problem, type=0, type_info=None, submit_time=None):
        if not submit_time:
            submit_time = int(time.time())
        self.code = code
        self.language = language
        self.user = user
        self.problem = problem
        self.submit_time = submit_time

        self.type = type
        self.type_info = type_info

        self.score = 0
        self.status = "Waiting"
        self.result = '{"status": "Waiting", "total_time": 0, "total_memory": 0, "score":0, "case_num": 0}'

    def __repr__(self):
        print "<JudgeState %r>" % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def is_allowed_see_result(self, user=None):
        if user and user.is_admin:
            return True
        if user and user.id == self.problem.user.id:
            return True

        if self.type == 0:
            return True
        elif self.type == 1:
            contest = Contest.query.filter_by(id=self.type_info).first()
            if contest.is_running():
                return False
            else:
                return True
        elif self.type == 2:
            if user and self.user == user.id:
                return True
            else:
                return False

        return False

    def is_allowed_see_code(self, user=None):
        if user and user.is_admin:
            return True
        if user and user.id == self.problem.user.id:
            return True

        if self.type == 0:
            return True
        elif self.type == 1:
            contest = Contest.query.filter_by(id=self.type_info).first()
            if contest.is_running():
                if user and self.user == user:
                    return True
                else:
                    return False
            else:
                return True
        elif self.type == 2:
            if user and self.user == user.id:
                return True
            else:
                return False

        return False

    def get_result(self):
        return json.loads(self.result)

    def update_result(self, result):
        self.score = result["score"]
        self.status = result["status"]
        self.result = json.dumps(result)

    def update_related_info(self):
        if self.type == 0:
            self.user.refresh_submit_info()
            self.user.save()

            self.problem.submit_num += 1
            if self.status == "Accepted":
                self.problem.ac_num += 1
            self.problem.save()
        elif self.type == 1:
            contest = Contest.query.filter_by(id=self.type_info).first()
            contest.new_submission(self)
    
    def update_userac_info(self):
        if self.type == 0:
            all_user_ac = UserAcProblem.query.filter_by(user_id = self.user.id).all()
            for ac_info in all_user_ac:
                if ac_info.problem_id == self.problem.id:
                    if ac_info.is_accepted and self.status != "Accepted":
                        return
                        
                    new_ac_info = UserAcProblem(user_id = ac_info.user_id, problem_id = ac_info.problem_id, judge_id = self.id)
                    ac_info.delete()
                    
                    if self.status == "Accepted":
                        new_ac_info.is_accepted = True
                    else:
                        new_ac_info.is_accepted = False
                    new_ac_info.save()
                    return
            
            new_ac_info = UserAcProblem(user_id = self.user.id, problem_id = self.problem.id, judge_id = self.id)
            if self.status == "Accepted":
                new_ac_info.is_accepted = True
            else:
                new_ac_info.is_accepted = False
            new_ac_info.save()
            return


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
