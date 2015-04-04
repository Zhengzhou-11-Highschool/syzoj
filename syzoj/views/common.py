from flask import redirect, url_for, request, render_template
from syzoj import oj
import time


def show_error(error, next):
    return redirect(url_for("error", info=error, next=next))


def need_login():
    return show_error("Please login first.", url_for("login"))


def not_have_permission():
    return show_error("You don't have permission", url_for("index"))


def pretty_time(now):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))

class Paginate():
    query = None
    total_page = 0
    per_page = 10
    cur_page = 1
    edge_display_num = 10
    make_url = None
    other = None

    def __init__(self, query, make_url, other=None, cur_page=1, per_page=10, edge_display_num=2):
        if not cur_page:
            cur_page = 1
        self.cur_page = int(cur_page)
        self.per_page = per_page
        self.edge_display_num = edge_display_num
        self.query = query
        self.make_url = make_url
        self.other = other
        total = query.count()
        self.total_page = total / per_page
        if total % per_page:
            self.total_page += 1


    def have_pre(self, cur_page=None):
        if not cur_page:
            cur_page = self.cur_page
        print cur_page > 1
        return cur_page > 1


    def have_next(self, cur_page=None):
        if not cur_page:
            cur_page = self.cur_page
        return cur_page < self.total_page


    def need_omit_left(self):
        return self.cur_page - self.edge_display_num > 1


    def need_omit_right(self):
        return self.cur_page + self.edge_display_num < self.total_page


    def range(self):
        start = self.cur_page - self.edge_display_num
        stop = self.cur_page + self.edge_display_num + 1
        if start < 1:
            start = 1
        if stop > self.total_page + 1:
            stop = self.total_page + 1
        return range(start, stop)


    def get(self):
        return self.query.offset((self.cur_page - 1) * self.per_page).limit(self.per_page)


    def get_html(self):
        pre_disable = ""
        next_disable = ""
        left_omit = ""
        right_omit = ""
        pre_url = ""
        next_url = ""
        pid_list = ""

        if self.have_pre():
            pre_url = self.make_url(self.cur_page - 1, self.other)
        else:
            pre_disable = "am-disabled"
        if self.have_next():
            next_url = self.make_url(self.cur_page + 1, self.other)
        else:
            next_disable = "am-disabled"

        if self.need_omit_left():
            left_omit = '''<li><span>...</span></li>'''
        if self.need_omit_right():
            right_omit = '''<li><span>...</span></li>'''

        for pid in self.range():
            active = ""
            if pid == self.cur_page:
                active = "am-active"
            pid_list += '''<li class="''' + active + '''"><a href="''' + self.make_url(pid,
                                                                                       self.other) + '''">''' + str(
                pid) + '''</a></li>'''

        html = '''<div class="am-u-sm-12">
        <ul class="am-pagination am-pagination-centered">
            <li class="''' + pre_disable + '''">
                <a href="''' + pre_url + '''"><span class="am-icon-angle-double-left"></span></a>
            </li>
            ''' + left_omit + pid_list + right_omit + '''
            <li class="''' + next_disable + '''">
                <a href="''' + next_url + '''"><span class="am-icon-angle-double-right"></span></a>
            </li>
        </ul>
    </div>'''
        return html

