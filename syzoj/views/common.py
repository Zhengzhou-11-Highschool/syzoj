import time

from flask import redirect, url_for


def show_error(error, next):
    return redirect(url_for("error", info=error, next=next))


def need_login():
    return show_error("Please login first.", url_for("login"))


def not_have_permission():
    return show_error("You don't have permission", url_for("index"))