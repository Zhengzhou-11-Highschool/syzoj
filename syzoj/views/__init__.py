from flask import request, render_template

from syzoj import oj,db
from syzoj.models import User
from syzoj.controller import Tools, Paginate
from .session import sign_up, login
from .problem import problem, problem_set
from .judge import submit_code, judge_state
from .user import user, edit_user
from .discussion import edit_article, article, discussion
from .contest import contest_list


@oj.route("/")
def index():
    query = User.query.order_by(db.desc(User.ac_num))
    ranker = Paginate(query, cur_page=1,  per_page=10)
    return render_template("index.html", tool=Tools, tab="index", ranker=ranker)


@oj.route("/error")
def error():
    info = request.args.get("info")
    next = request.args.get("next")
    #TODO:rewrite error page for beautiful
    return render_template("error_info.html", tool=Tools, info=info, next=next)