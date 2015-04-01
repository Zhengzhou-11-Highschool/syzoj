from flask import Flask, jsonify, redirect, url_for, escape, abort, request, render_template
from syzoj import oj
from syzoj.models import User, Problem, get_problem_by_id, File, JudgeState,WaitingJudge, get_user, Article
from syzoj.views.common import need_login, not_have_permission, show_error,pretty_time
import os

@oj.route("/article/<int:article_id>")
def article(article_id):
    article=Article.query.filter_by(id=article_id).first()
    if not article:
        return show_error("Can't find article",url_for('index'))
    print article.title
    return render_template("article.html",article=article,user=get_user(),pretty_time=pretty_time)

@oj.route("/article/<int:article_id>/edit",methods=["GET", "POST"])
def edit_article(article_id):
    user = get_user()
    if not user:
        return need_login()

    article = Article.query.filter_by(id=article_id).first()
    if article and article.is_allowed_edit(user) == False:
        return not_have_permission()

    if request.method=="POST":
        if request.form.get("title")=="" or request.form.get("content")=="":
            return show_error("Please input title and content",
                              url_for("edit_article", article_id=article_id))
        if not article:
            article=Article(title=request.form.get("title"),content=request.form.get("content"),user=user)

        article.title=request.form.get("title")
        article.content=request.form.get("content")
        article.save()
        return redirect(url_for("article",article_id=article_id))
    else:
        return render_template("edit_article.html",user=get_user(),article=article)