from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker


class Schema():

    def __init__(self, engine):

        self.engine = engine
        self.meta = MetaData(bind=self.engine)
        self.meta.reflect()

        self.Session = sessionmaker(bind=self.engine)

    def __getattr__(self, table_name):

        return self.meta.tables[table_name]

    def execute(self, *args, **kwargs):
        with self.session() as session:
            session.execute(*args, **kwargs)

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

    @classmethod
    def from_params(cls, *args, **kwargs):
        engine = create_engine(*args, **kwargs)

        return cls(engine)
