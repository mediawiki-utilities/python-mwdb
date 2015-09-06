from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


class Schema():

    def __init__(self, engine_or_url, *args, **kwargs):

        if isinstance(engine_or_url, Engine):
            self.engine = engine_or_url
        else:
            self.engine = create_engine(engine_or_url, *args, **kwargs)

        self.meta = MetaData(bind=self.engine)
        self.meta.reflect(views=True)

        self.Session = sessionmaker(bind=self.engine)

    def __getattr__(self, table_name):

        return self.meta.tables[table_name]

    def execute(self, *args, **kwargs):
        with self.session() as session:
            return session.execute(*args, **kwargs)

    @contextmanager
    def session(self):
        """Provides a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
