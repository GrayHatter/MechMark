import socket
import datetime as dt
import regex as re

from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, current_user

# from ..auth import auth_required
from mechmark.db import db
from mechmark.valid import Validate
from mechmark.types.Users import User
from mechmark.config import cfg
from mechmark.email_ import Send_email


users = Blueprint('users', __name__)


@users.route('/Login/Token/<token>')
def login_token(token):
    if current_user:
        logout_user()

    usr = User.q.filter(User.token == token).one_or_none()
    if not usr:
        return render_template("login_token_invalid.html")

    login_user(usr)
    return redirect('/')


@users.route('/Login')
def login():
    return render_template("login.html")


def _msg(token):
    return ('Click on the following link to login to MechMark On this system\n\n'
        f'https://{cfg.get("app", "domain")}/Login/Token/{token}\n')


@users.route('/Login/Send', methods=['POST'])
def login_send():
    v = Validate(request)
    user = v.require('user')
    usr = User.q.filter(User.username.ilike(user)).one_or_none()
    v.expect(usr is not None, "Sorry, User Does not exist.", 'user')
    if not v.ok:
        return render_template("login.html", valid=v)

    if usr.token_time is None or usr.token_time < dt.datetime.utcnow() - dt.timedelta(hours=2):
        token = usr.new_token()
        usr.last_email = dt.datetime.utcnow()
        db.session.commit()
        Send_email([usr.email], "MechMark Login Token", _msg(token))

    return render_template("login_sent.html")


@users.route('/Logout')
def logout():
    logout_user()
    return redirect("/")


@users.route('/Register')
def register():
    return render_template('register.html')


@users.route('/Register/Send', methods=['POST'])
def register_submit():
    v = Validate(request)
    email = v.require('email')
    user = v.require('user')
    if not v.ok:
        return render_template("register.html", valid=v)

    user, number = re.subn(r'[^a-zA-Z0-9_-]', '', user)
    v.expect(number == 0,
        "Invalid symbol in Username, Username can only contain ASCII letters, numbers, dashes, and underscores.", 'user')
    v.expect(len(user) > 3, "Username Too short", 'user')
    v.expect(len(user) and user[0] != '_', "Username can not start with an underscore.", 'user')
    if not v.ok:
        return render_template("register.html", valid=v)

    usr = User.query.filter(User.username.ilike(user)).one_or_none()
    v.expect(usr is None, "Username taken", 'user')
    if not v.ok:
        return render_template("register.html", valid=v)

    usr = User(username=user)
    usr.email = email
    usr.nickname = v.optional('nick')
    usr.discord = v.optional('discord')
    usr.postal = v.optional('postal')

    msg = "Unable to find this domain to send and email to. If the email address is valid, please open an issue."
    try:
        name, host = email.split('@', 1)
        addr = socket.gethostbyname(host)
        v.expect(addr is not None, msg, 'email')
    except socket.gaierror:
        v.expect(False, msg, 'email')

    if not v.ok:
        return render_template("register.html", valid=v)

    db.session.add(usr)
    db.session.commit()

    login_user(usr)
    return redirect("/")


