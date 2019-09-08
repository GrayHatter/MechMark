import regex as re

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from secrets import token_urlsafe
from PIL import Image
from math import floor

from mechmark.auth import auth_required
from mechmark.db import db
from mechmark.config import cfg
from mechmark.valid import Validate
from mechmark.types.Boards import Board, BoardImage, BoardTag, BoardPart
from mechmark.types.Parts import Part


boards = Blueprint('boards', __name__)


def _get_boards(filter, num):
    return Board.q.all()


@boards.route('/Filter', methods=["POST"])
def filter_POST(s):
    v = Validate(request)
    s = v.require('filter')
    if v.err:
        return redirect(url_for('.index'))
    return render_template("boards.html", boards=_get_boards(s, 0))


@boards.route('/Filter/<s>')
def filter(s):
    return render_template("boards.html", boards=_get_boards(None, 0))


@boards.route('/Page/<int:num>')
def page(num):
    return render_template("boards.html", boards=_get_boards(None, 0))


@boards.route('')
def index():
    return page(0)


@boards.route('/New')
def new():
    return render_template('boards_new.html')


@boards.route('<name>')
def name(name):
    name, number = re.subn(r'\s', '_', name.strip())
    if number:
        return redirect(url_for('.name', name=name))

    board = Board.q.filter(Board.name == name).one_or_none()
    return render_template('boards_view.html', board=board)


@boards.route('/<name>/Part/Add', methods=['POST'])
@auth_required()
def part_add_POST(name):
    name, number = re.subn(r'\s', '_', name.strip())
    if number:
        return redirect(url_for('.name', name=name))

    board = Board.q.filter(Board.name == name).one_or_none()
    if not board:
        redirect(url_for('index'))

    v = Validate(request)
    name_num = v.require('name_num')
    count = v.optional('count', "0")
    optional = v.optional('optional', "1")
    note = v.optional('note')

    part = Part.q.filter(Part.num.ilike(name_num)).one_or_none()
    if part is None:
        part = Part.q.filter(Part.name.ilike(name_num)).first()

    v.expect(part is not None, "Couldn't find this part, do you need to create it first?", 'name_num')
    if v.err:
        return render_template('boards_view.html', board=board, valid=v)

    board_part = BoardPart()
    board_part.board = board
    board_part.owner = current_user
    board_part.part = part
    board_part.note = note
    try:
        board_part.optional = int(optional)
    except Exception:
        board_part.optional = True
    board_part.count = count

    db.session.add(board_part)
    db.session.commit()

    return redirect(url_for('.name', name=name))


@boards.route('/New/Send', methods=['POST'])
@auth_required()
def new_POST():
    v = Validate(request)
    name = v.require('name')

    if v.err:
        return render_template('boards_new.html', valid=v)

    board = Board.q.filter(Board.name == name).one_or_none()
    v.expect(board == None, f"{name} already exists, please choose another. (Perhaps it's {name} v2?)", "name")

    if v.err:
        return render_template('boards_new.html', valid=v)

    name = re.sub(r'\s', '_', name.strip())
    board = Board(name=name)
    board.user = current_user
    board.conicalurl = v.optional('url')
    board.buildguide = v.optional('build')
    board.owner = current_user
    db.session.add(board)

    for tag in v.optional('tags').split(','):
        tag_name = tag.strip()
        if len(tag_name):
            t = BoardTag(name=tag_name)
            t.owner = current_user
            t.board = board
            db.session.add(t)

    photo = v.file('photo')
    if photo:
        boardimg = BoardImage(title=photo.filename, location=f"{token_urlsafe(10)}.png")
        boardimg.board = board
        boardimg.owner = current_user

        img = Image.open(v.file('photo').stream)
        if img.width > img.height:
            img = img.resize((floor(img.width * (500 / img.width)), floor(img.height * (500 / img.width))))
        else:
            img = img.resize((floor(img.width * (500 / img.height)), floor(img.height * (500 / img.height))))
        img.save(f"{cfg.get('app', 'file_upload_dir')}/{boardimg.location}")

        db.session.add(boardimg)

    db.session.commit()

    return redirect(url_for('.index'))
