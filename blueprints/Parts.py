from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from mechmark.auth import auth_required
from mechmark.db import db
from mechmark.valid import Validate
from mechmark.types.Parts import Part

parts = Blueprint('parts', __name__)


@parts.context_processor
def inject():
    return {
        'url_for': url_for
    }


def _get_parts(filter, num):
    return Part.q.all()


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


@parts.route('<int:id_>')
def view(id_):
    part = Part.q.filter(Part.id == id_).one_or_none()
    if part is None:
        return redirect(url_for('.index'))

    return render_template("parts_view.html", part=part)


@parts.route('<int:id_>/Stock/Add')
def stock_add(id_):
    part = Part.q.filter(Part.id == id_).one_or_none()
    if part is None:
        return redirect(url_for('.index'))

    return render_template("parts_view.html", part=part)


@parts.route('<int:id_>/Edit')
def edit(id_):
    part = Part.q.filter(Part.id == id_).one_or_none()
    if part is None:
        return redirect(url_for('.index'))

    return render_template("parts_view.html", part=part)


@parts.route('/New')
def new():
    return render_template('parts.html', parts=_get_parts(None, 0))


@parts.route('/New/Send', methods=['POST'])
@auth_required()
def new_POST():
    v = Validate(request)
    name = v.optional('name')
    number = v.optional('number')

    v.expect(name or number, "Name, and Number, both can't be empty")
    if v.err:
        return render_template('parts.html', parts=_get_parts(None, 0))

    part = Part.q.filter(Part.num == number.strip()).one_or_none()
    v.expect(part is None, "This part number already exists", "number")
    if v.err:
        return render_template('parts.html', parts=_get_parts(None, 0))

    part = Part(name=name, num=number)
    part.owner = current_user

    db.session.add(part)
    db.session.commit()

    return render_template('parts.html', parts=_get_parts(None, 0))
