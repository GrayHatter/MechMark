import datetime as dt

from secrets import token_urlsafe

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Unicode
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import CIDR, UUID

from mechmark.db import Base


class UserAuth(Base):
    __tablename__ = 'user_auth'
    # __table_args__ = (UniqueConstraint('user_id', 'factor_type', name='user_2fa_uid_factortyp_key'),)
    id = Column(Integer, primary_key=True)

    # user_id = Column(Integer, ForeignKey('users.id'))
    # factor_type = Column(Text, default='totp')
    # secret = Column(UUID)

    # user = relationship('Users', back_populates='user_2fas')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(DateTime, default=None)

    username = Column(Unicode, unique=True)
    nickname = Column(Unicode)
    email = Column(String(256))
    last_email = Column(DateTime, default=None)

    token = Column(Unicode)
    token_time = Column(DateTime, default=None)

    postal = Column(String, default=0)
    bio = Column(Text)
    default_currency = Column(String)

    discord_id = Column(BigInteger)
    discord_name = Column(Unicode)
    discord_key = Column(UUID)

    last_ip = Column(CIDR)

    def __repr__(self):
        return '<User Object for {}>'.format(self.username)

    @hybrid_property
    def q(self):
        if hasattr(self, 'query'):
            return self.query.filter(self.deleted == None)
        return None

    # flask -_-
    def is_authenticated(self):
        return self.deleted == None

    def is_active(self):
        return self.deleted == None

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def new_token(self):
        self.token = token_urlsafe(32)
        self.token_time = dt.datetime.utcnow()
        return self.token
