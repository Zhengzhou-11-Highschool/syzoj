from syzoj import db
from syzoj.models.problem import Problem
import time
import json


class ContestRanklist(db.Model):
    """
    save ranklist as json
    follow is ranklist structure
    {
        "player_num": player_num
        1: the ContestPlayer's id of rank1
        2: the ContestPlayer's id of rank2
        ...
    }
    """
    id = db.Column(db.Integer, primary_key=True)
    ranklist = db.Column(db.Text)

    def __init__(self):
        ranklist = {"player_num": 0}
        self.ranklist = json.dumps(ranklist)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_players(self):
        ranklist = json.loads(self.ranklist)
        players = []
        for i in range(ranklist["player_num"]):
            player = ContestPlayer.query.filter_by(id=ranklist[str(i)]).first()
            players.append(player)
        return players

    def update(self, new_player=None):
        players = self.get_players()
        if not new_player in players:
            players.append(new_player)

        players.sort(key = lambda p: p.score, reverse = True)
        # players.sort(cmp=lambda x, y: x.score > y.score or (x.score == y.score and x.time_spent < y.time_spent))

        ranklist = {"player_num": len(players)}
        for rank, player in enumerate(players):
            ranklist[rank] = player.id

        self.ranklist = json.dumps(ranklist)


class ContestPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey("contest.id"), index=True)
    contest = db.relationship("Contest", backref=db.backref("players", lazy="dynamic"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("contests", lazy="dynamic"))

    score = db.Column(db.Integer)
    score_details = db.Column(db.Text)
    time_spent = db.Column(db.Integer)

    def __init__(self, contest_id, user_id):
        self.contest_id = contest_id
        self.user_id = user_id

        self.score = 0
        self.time_spent = 0
        self.score_details = ""

    def __repr__(self):
        return "<ContestPlayer contest_id:%s user_id=%s score_details=%s>" % \
               (self.contest_id, self.user_id, self.score_details)

    def update_score(self, problem, score, judge_id):
        score_details = {}
        if self.score_details:
            score_details = json.loads(self.score_details)
        pid = str(problem.id)
        score_details[pid] = {}
        score_details[pid]["score"] = score
        score_details[pid]["judge_id"] = judge_id
        score_details["score"] = 0
        for key, val in score_details.iteritems():
            if isinstance(val, dict):
                score_details["score"] += val["score"]
        self.score = score_details["score"]
        self.time_spent = problem.submit_num
        self.score_details = json.dumps(score_details)

    def get_score_details(self):
        return json.loads(self.score_details)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    start_time = db.Column(db.Integer)  # goodbye at 2038-1-19
    end_time = db.Column(db.Integer)

    holder_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    holder = db.relationship("User", backref=db.backref("hold_contests", lazy='dynamic'))

    information = db.Column(db.Text)
    # save use text represent problems id,split by "|"
    # for example use "2|23|123" represent this contest use problems which id equal 2\23 or 123
    problems = db.Column(db.Text)

    ranklist_id = db.Column(db.Integer, db.ForeignKey("contest_ranklist.id"), index=True)
    ranklist = db.relationship("ContestRanklist", backref=db.backref("contests", lazy="dynamic"))

    def __init__(self, title, start_time, end_time, holder):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.holder = holder

        ranklist = ContestRanklist()
        self.ranklist = ranklist

    def __repr__(self):
        return "<Contest %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()

    def is_allowed_edit(self, user=None):
        if user and user.have_privilege(4):
            return True
        if user and user.id == self.holder.id:
            return True
        return False

    def new_submission(self, judge):
        problems = self.get_problems()
        if judge.problem not in problems:
            pass
            return False

        player = self.players.filter_by(user_id=judge.user_id).first()
        if not player:
            player = ContestPlayer(self.id, judge.user_id)
        player.update_score(judge.problem, judge.score, judge.id)
        player.save()
        self.ranklist.update(player)
        self.ranklist.save()

    def is_running(self, now=None):
        if not now:
            now = int(time.time())
        return self.start_time <= now and now <= self.end_time

    def get_ranklist(self):
        return self.ranklist.ranklist

    def get_problems(self):
        if not self.problems:
            return []

        problems = []
        for pid in self.problems.split('|'):
            pid = int(pid)
            problems.append(Problem.query.filter_by(id=int(pid)).first())
        return problems

    def set_problems(self, problems_list):
        self.problems = ""
        for pid in problems_list:
            if Problem.query.filter_by(id=pid).first():
                if self.problems:
                    self.problems += '|'
                self.problems += str(pid)
            else:
                pass
                # TODO:raise error
