from flask import redirect, url_for


def show_error(error, next):
    return redirect(url_for("error", info=error, next=next))


def need_login():
    return show_error("Please login first.", url_for("login"))


def not_have_permission():
    return show_error("You don't have permission", url_for("index"))

class Paginate():
    query=None
    total_page=0
    per_page=10
    cur_page=1
    edge_display_num=10
    def __init__(self,query,cur_page=1,per_page=10,edge_display_num=2):
        if not cur_page:
            cur_page=1
        self.cur_page=int(cur_page)
        self.per_page=per_page
        self.edge_display_num=edge_display_num
        self.query=query
        total=query.count()
        self.total_page=total/per_page
        if total%per_page:
            self.total_page+=1

    def have_pre(self,cur_page=None):
        if not cur_page:
            cur_page=self.cur_page
        print cur_page>1
        return cur_page>1

    def have_next(self,cur_page=None):
        if not cur_page:
            cur_page=self.cur_page
        return cur_page<self.total_page

    def need_omit_left(self):
        return self.cur_page-self.edge_display_num > 1

    def need_omit_right(self):
        return self.cur_page+self.edge_display_num < self.total_page

    def range(self):
        start=self.cur_page-self.edge_display_num
        stop=self.cur_page+self.edge_display_num+1
        if start<1:
            start=1
        if stop>self.total_page+1:
            stop=self.total_page+1
        return range(start,stop)

    def get(self):
        return self.query.offset((self.cur_page-1)*self.per_page).limit(self.per_page)
