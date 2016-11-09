from syzoj import db
import time

tags_table = db.Table('article_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('article_tag.id'), index=True),
                      db.Column('article_id', db.Integer, db.ForeignKey('article.id'), index=True)
                      )


class ArticleTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ArticleTag %r>" % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("articles", lazy='dynamic'))

    public_time = db.Column(db.Integer)  # googbye at 2038-1-19
    update_time = db.Column(db.Integer)
    sort_time = db.Column(db.Integer, index=True)

    tags = db.relationship('ArticleTag', secondary=tags_table,
                           backref=db.backref('articles', lazy='dynamic'))

    comments_num = db.Column(db.Integer)
    allow_comment = db.Column(db.Boolean)

    def __init__(self, title, content, user, allow_comment=True, public_time=None):
        if not public_time:
            public_time = int(time.time())
        self.title = title
        self.content = content
        self.user = user
        self.public_time = public_time
        self.update_time = public_time
        self.sort_time = public_time
        self.comments_num = 0
        self.allow_comment = allow_comment


    def __repr__(self):
        return "<Article %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_allowed_edit(self, user=None):
        if not user:
            return False
        if user.id == self.user_id:
            return True
        if user.have_privilege(6):
            return True
        return False


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), index=True)
    article = db.relationship("Article", backref=db.backref("comments", lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("comments", lazy='dynamic'))

    public_time = db.Column(db.Integer)  # googbye at 2038-1-19

    def __init__(self, content, article, user, public_time=None):
        if not public_time:
            public_time = int(time.time())
        self.content = content
        self.article = article
        self.user = user
        self.public_time = public_time


    def __repr__(self):
        return "<Comment %r>" % self.content

    def save(self):
        db.session.add(self)
        db.session.commit()
