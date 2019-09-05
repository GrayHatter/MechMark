from flask import Blueprint, render_template, request, redirect, url_for

# from ..auth import auth_required
from mechmark.db import db
from mechmark.valid import Validate


parts = Blueprint('parts', __name__)


@parts.context_processor
def inject():
    return {
        'url_for': url_for
    }


def _get_parts(filter, num):
    # return Part.query.all()
    return []


@parts.route('/Filter', methods=["POST"])
def filter_POST(s):
    v = Validate(request)
    s = v.require('filter')
    if v.err:
        return redirect(url_for('.index'))
    return render_template("parts.html", parts=_get_parts(s, 0))


@parts.route('/Filter/<s>')
def filter(s):
    return render_template("parts.html", parts=_get_parts(None, 0))


@parts.route('/Page/<int:num>')
def page(num):
    return render_template("parts.html", parts=_get_parts(None, 0))


@parts.route('')
def index():
    return page(0)


@parts.route('/New')
def new():
    return render_template('parts.html', parts=_get_parts(None, 0))


@parts.route('/New/Send', methods=['POST'])
def new_POST():
    return render_template('parts.html', parts=_get_parts(None, 0))
