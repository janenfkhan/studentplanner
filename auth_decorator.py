from datetime import datetime
from flask import session
from functools import wraps
from flask import render_template, request, session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return render_template("loginrequired.html", time=datetime.now())
    return decorated_function