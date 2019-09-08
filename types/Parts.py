import regex as re

from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship


from ..db import Base


class Part(Base):
    __tablename__ = 'parts'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
    disabled = Column(DateTime, default=None)

    name = Column(String)
    num = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))

    tags = relationship("PartTag", uselist=True)
    stock = relationship("PartStock", uselist=True)
    sources = relationship("PartSource", uselist=True)


class PartTag(Base):
    __tablename__ = 'part_tagss'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))
    part_id = Column(Integer, ForeignKey('parts.id'))


class PartSource(Base):
    __tablename__ = 'part_sources'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
    disabled = Column(DateTime, default=None)

    owner_id = Column(Integer, ForeignKey('users.id'))
    part_id = Column(Integer, ForeignKey('parts.id'))

    cost = Column(Integer)
    currency = Column(String)


class PartStock(Base):
    __tablename__ = 'part_stock'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
    disabled = Column(DateTime, default=None)

    owner_id = Column(Integer, ForeignKey('users.id'))
    part_id = Column(Integer, ForeignKey('parts.id'))

    count = Column(Integer)
    cost = Column(Integer)
    currency = Column(String)

