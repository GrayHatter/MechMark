from functools import wraps
from flask import redirect
from flask_login import current_user, logout_user

from mechmark.db import db
from mechmark.types import Users


def auth_required(required_auth=None):
    def wrap(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user:
                if required_auth is None:
                    return f(*args, **kwargs)
                else:
                    if current_user.auth(required_auth):
                        return f(*args, **kwargs)
                    else:
                        print(f'{current_user.username} force logout')
                        logout_user()
            return redirect('/Login')
        return wrapped
    return wrap
