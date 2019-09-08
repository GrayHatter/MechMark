from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.hybrid import hybrid_property

from werkzeug.local import LocalProxy

from datetime import datetime


_db = None
db = LocalProxy(lambda: _db)


@as_declarative()
class Base(object):
    @hybrid_property
    def q(self):
        if hasattr(self, 'query'):
            if hasattr(self, 'deleted'):
                return self.query.filter(self.deleted == None)

            return self.query
        return None


class DBSession():
    def __init__(self, conn_str, assign_global=True):
        global Base, _db
        self.engine = create_engine(conn_str, isolation_level="READ COMMITTED")
        self.session = scoped_session(sessionmaker(autocommit=False, bind=self.engine))
        Base.query = self.session.query_property()
        if assign_global:
            _db = self

    def init(self):
        @event.listens_for(Base, 'before_insert', propagate=True)
        def before_insert(mapper, connection, target):
            if hasattr(target, 'created'):
                target.created = datetime.utcnow()
            if hasattr(target, 'updated'):
                target.updated = datetime.utcnow()

        @event.listens_for(Base, 'before_update', propagate=True)
        def before_update(mapper, connection, target):
            if hasattr(target, 'updated'):
                target.updated = datetime.utcnow()

    def create(self):
        Base.metadata.create_all(bind=self.engine)
