from syzoj import db
from syzoj.models.file import File

tags_table = db.Table('problem_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('problem_tag.id'), index=True),
                      db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'), index=True)
                      )


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(80), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("upload_problems", lazy='dynamic'))

    description = db.Column(db.Text)
    input_format = db.Column(db.Text)
    output_format = db.Column(db.Text)
    example = db.Column(db.Text)
    limit_and_hint = db.Column(db.Text)

    time_limit = db.Column(db.Integer)
    memory_limit = db.Column(db.Integer)

    testdata_id = db.Column(db.Integer, db.ForeignKey("file.id"))
    testdata = db.relationship("File", backref=db.backref('problems', lazy='dynamic'))

    tags = db.relationship('ProblemTag', secondary=tags_table,
                           backref=db.backref('problems', lazy='dynamic'))

    ac_num = db.Column(db.Integer)
    submit_num = db.Column(db.Integer)
    is_public = db.Column(db.Boolean)

    def __init__(self, title, user,
                 description="", input_format="", output_format="", example="", limit_and_hint="",
                 time_limit=1000, memory_limit=128
                 ):
        self.title = title
        self.user = user

        self.description = description
        self.input_format = input_format
        self.output_format = output_format
        self.example = example
        self.limit_and_hint = limit_and_hint

        self.time_limit = time_limit
        self.memory_limit = memory_limit

        self.ac_num = 0
        self.submit_num = 0
        self.is_public = False

    def __repr__(self):
        return "<Problem %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, title=None, description=None, input_format=None, output_format=None, limit_and_hint=None):
        if title != None:
            self.title = title
        if description != None:
            self.description = description
        if input_format != None:
            self.input_format = input_format
        if output_format != None:
            self.output_format = output_format
        if limit_and_hint != None:
            self.limit_and_hint = limit_and_hint

    def update_testdata(self, file):
        td_name = "testdata_%d" % self.id
        td = File.query.filter_by(filename=td_name).first()
        if not td:
            td = File(file)
        td.file = file
        td.filename = td_name
        td.save_file()
        td.save()
        self.testdata = td

    def is_allowed_edit(self, user):
        if not user:
            return False
        if self.user_id == user.id or user.is_admin:
            return True
        return False

    def is_allowed_use(self, user):
        if self.is_public:
            return True
        if not user:
            return False
        if self.user_id == user.id or user.is_admin:
            return True
        # TODO:if it belong a contest  and contest is running,also allow to use
        return False

    def set_is_public(self, public):
        self.is_public = public
        self.save()


class ProblemTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag %r>" % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()
