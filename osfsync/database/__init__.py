import logging
import contextlib
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from osfsync.database.models import Base, User, Node, File
from osfsync.settings import PROJECT_DB_FILE

CORE_OSFO_MODELS = [User, Node, File]
URL = 'sqlite:///{}'.format(PROJECT_DB_FILE)

engine = create_engine(URL, connect_args={'check_same_thread': False}, )
Base.metadata.create_all(engine)
_session = sessionmaker(bind=engine)()
_session_rlock = threading.RLock()
logger = logging.getLogger(__name__)


@contextlib.contextmanager
def Session():
    with _session_rlock:
        yield _session


def drop_db():
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


def clear_models():
    with Session() as session:
        for model in CORE_OSFO_MODELS:
            session.query(model).delete()
