import regex as re

from sqlalchemy import func
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
# from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from ..db import Base


class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String, nullable=False, unique=True)
    conicalurl = Column(String)
    buildguide = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship("User")
    images = relationship("BoardImage", back_populates='board', uselist=True, order_by="desc(BoardImage.created)")
    tags = relationship("BoardTag", uselist=True)

    parts = relationship("BoardPart")

    @hybrid_property
    def q(self):
        if hasattr(self, 'query'):
            return self.query
        return None

    @hybrid_property
    def primary_image(self):
        if len(self.images) == 0:
            return None
        return self.images[0]

    @hybrid_property
    def html_name(self):
        return re.sub(r'\s', '_', self.name)


class BoardImage(Base):
    __tablename__ = 'board_images'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    title = Column(String)
    location = Column(String)

    board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    board = relationship("Board")
    owner = relationship("User")


class BoardTag(Base):
    __tablename__ = 'board_tags'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String)

    board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class BoardPart(Base):
    __tablename__ = 'board_parts'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    part_id = Column(Integer, ForeignKey('parts.id'))
    board_id = Column(Integer, ForeignKey('boards.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))

    count = Column(Integer)
    optional = Column(Boolean)
    note = Column(String)

    board = relationship('Board')
    part = relationship('Part')
    owner = relationship('User')

    @hybrid_property
    def name(self):
        return self.part.name

    @hybrid_property
    def num(self):
        return self.part.num


class BoardWorkList(Base):
    __tablename__ = 'board_work_lists'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    name = Column(String)
    public = Column(Boolean)


class BoardWorkListPart(Base):
    __tablename__ = 'board_work_list_parts'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    worklist_id = Column(Integer, ForeignKey('board_work_lists.id'))
    worklist = None
