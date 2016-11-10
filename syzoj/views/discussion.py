# -*- coding: utf-8 -*-
import time
from urllib import urlencode

from flask import redirect, url_for, request, render_template, abort

from syzoj import oj
from syzoj.models import User, Article, Comment
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error


@oj.route("/discussion")
def discussion():
    query = Article.query.order_by(Article.sort_time.desc())

    def make_url(page, other):
        return url_for("discussion") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=10)
    return render_template("discussion.html", tool=Tools, tab="discussion", sorter=sorter)


@oj.route("/article/<int:article_id>")
def article(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if not article:
        return show_error("找不到文章", url_for('index'))

    comments = Comment.query.filter_by(article_id=article_id)
    comments_num = comments.count()

    def make_url(page, other):
        return url_for("article", article_id=article_id) + "?" + urlencode({"page": page})
    sorter = Paginate(comments, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=10)

    return render_template("article.html", tool=Tools, article=article,
                           comment_num=comments_num, sorter=sorter, tab="discussion")


@oj.route("/article/<int:article_id>/edit", methods=["GET", "POST"])
def edit_article(article_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    article = Article.query.filter_by(id=article_id).first()
    if article and article.is_allowed_edit(user) == False:
        return not_have_permission()

    if request.method == "POST":
        if request.form.get("title") == "" or request.form.get("content") == "":
            return show_error("Please input title and content",
                              url_for("edit_article", article_id=article_id))
        if not article:
            article = Article(title=request.form.get("title"), content=request.form.get("content"), user=user)

        article.title = request.form.get("title")
        article.content = request.form.get("content")
        article.update_time = time.time()
        article.sort_time = time.time()
        article.save()
        return redirect(url_for("article", article_id=article.id))
    else:
        return render_template("edit_article.html", tool=Tools, article=article, tab="discussion")


@oj.route("/article/<int:article_id>/delete")
def delete_article(article_id):
    user = User.get_cur_user()
    article = Article.query.filter_by(id=article_id).first()

    if not user:
        return need_login()

    if not article:
        return show_error("Can't find article", url_for('index'))

    if article and article.is_allowed_edit(user) == False:
        return not_have_permission()

    if request.args.get("confirm") == "true":
        article = Article.query.filter_by(id=article_id).first()
        if article and article.is_allowed_edit(user) == False:
            return not_have_permission()

        if article:
            article.delete()
        return redirect(url_for("discussion"))
    else:
        return render_template("delete_article.html", tool = Tools, user=user, article=article)


@oj.route("/article/<int:article_id>/comment", methods=["POST"])
def comment_article(article_id):
    user = User.get_cur_user()
    article = Article.query.filter_by(id=article_id).first()
    if not article:
        abort(404)
    if not user:
        return need_login()

    comment_str = request.form.get("comment")
    if not comment_str.replace(" ", ""):
        return show_error("请输入评论",
                          next=url_for("article", article_id=article_id))

    comment = Comment(comment_str, article, user)
    comment.save()

    return redirect(url_for("article", article_id=article.id))
