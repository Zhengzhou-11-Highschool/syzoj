from syzoj import db
from random import randint
import time

tags_table = db.Table('problem_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('problem_tag.id')),
                      db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
                      )


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("upload_problems", lazy='dynamic'))

    description = db.Column(db.Text)
    input_format = db.Column(db.Text)
    output_format = db.Column(db.Text)
    example = db.Column(db.Text)
    limit_and_hint = db.Column(db.Text)

    time_limit = db.Column(db.Integer)
    memory_limit = db.Column(db.Integer)

    tags = db.relationship('ProblemTag', secondary=tags_table,
                           backref=db.backref('problems', lazy='dynamic'))

    ac_num = db.Column(db.Integer)
    submit_num = db.Column(db.Integer)
    is_public = db.Column(db.Boolean)

    def __init__(self, title, user,
                 description=None, input_format=None, output_format=None, example=None, limit_and_hint=None,
                 time_limit=None, memory_limit=None,
                 tags=None):
        self.title = title
        self.user = user

        self.description = description
        self.input_format = input_format
        self.output_format = output_format
        self.example = example
        self.limit_and_hint = limit_and_hint

        time_limit = time_limit
        memory_limit = memory_limit
        self.tags = tags
        self.ac_num = 0
        self.submit_num = 0
        self.is_public = False

    def __repr__(self):
        return "<Problem %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()


class ProblemTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag %r>" % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()