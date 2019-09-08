import os
import datetime as dt

import flask
from flask import redirect, request, render_template, url_for, session
from flask_login import LoginManager, current_user

from jinja2 import FileSystemLoader, ChoiceLoader

from mechmark.valid import Validate, HTML_CSRFT
from mechmark.db import DBSession
from mechmark.config import Configuration
from mechmark.types.Users import User
from mechmark.types.Boards import Board
from mechmark.types.Parts import Part

from mechmark.blueprints.Users import users
from mechmark.blueprints.Parts import parts
from mechmark.blueprints.Boards import boards

from uwsgidecorators import postfork, lock

app = flask.Flask(__name__)
cfg = Configuration('./mechmark/config.ini')
db = None

app.secret_key = cfg.get('app', 'secret_key')
app.jinja_env.cache = None
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.jinja_env.keep_trailing_newline = False
app.jinja_loader = ChoiceLoader([
    FileSystemLoader("templates"),
    FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
])
app.register_blueprint(users)
app.register_blueprint(parts, url_prefix='/Parts')
app.register_blueprint(boards, url_prefix='/Boards')
@app.teardown_appcontext
def expire_db(err):
    db.session.expire_all()


@postfork
@lock
def fix_db():
    global db
    db = DBSession(f"postgresql+psycopg2://"
        f"{cfg.get('DB', 'user')}:"
        f"{cfg.get('DB', 'pass')}@"
        f"{cfg.get('DB', 'host')}/"
        f"{cfg.get('DB', 'name')}")
    db.init()
    db.create()


@app.context_processor
def inject():
    return {
        'request': request,
        'valid': Validate(request, require_csrft=False),
        'dt': dt,
        'str': str,
        'current_user': current_user,
        'cfg': cfg,
        'csrft_input': HTML_CSRFT(session),
        'url_for': url_for,
    }


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = lambda: None


@login_manager.user_loader
def load_user(username):
    return User.q.filter(User.username.ilike(username)).one_or_none()


@app.route('/favicon.ico')
def icon():
    return redirect('/static/favicon.ico', code=301)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/FAQ')
def faq():
    return render_template("faq.html")
