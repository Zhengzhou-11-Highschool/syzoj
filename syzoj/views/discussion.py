from urllib import urlencode

from flask import redirect, url_for, request, render_template

from syzoj import oj
from syzoj.models import User, Article
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error


@oj.route("/discussion")
def discussion():
    query = Article.query

    def make_url(page, other):
        return url_for("discussion") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=3, per_page=10)
    return render_template("discussion.html", tool=Tools, tab="discussion", sorter=sorter)


@oj.route("/article/<int:article_id>")
def article(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if not article:
        return show_error("Can't find article", url_for('index'))

    return render_template("article.html", tool=Tools, article=article, tab="discussion")


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
        article.save()
        return redirect(url_for("article", article_id=article.id))
    else:
        return render_template("edit_article.html", user=User.get_cur_user(), article=article, tab="discussion")


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

        article.delete()
        return redirect(url_for("discussion"))
    else:
        return render_template("delete_article.html", user=user, article=article)