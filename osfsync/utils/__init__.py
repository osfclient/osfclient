import re
import hashlib
import os

from enum import Enum
from sqlalchemy.orm.exc import NoResultFound

from osfsync import settings
from osfsync.database import Session
from osfsync.database import models
from osfsync.exceptions import NodeNotFound
from osfsync.utils.authentication import get_current_user


IGNORE_RE = re.compile(r'.*{}({})'.format(re.escape(os.path.sep), '|'.join(settings.IGNORED_PATTERNS)))


class EventType(Enum):
    CREATE = 0
    DELETE = 1
    MOVE = 2
    UPDATE = 3


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def hash_file(path, *, chunk_size=65536):
    """
    Return the SHA256 hash of a file

    :param pathlib.Path path:
    :param int chunk_size: Read chunk size, in bytes
    :return:
    """
    s = hashlib.sha256()
    with path.open(mode='rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            s.update(chunk)
    return s.hexdigest()


def extract_node(path):
    """Given a file path extract the node id and return the loaded Database object
    Visual, how this method works:
        '/root/OSF/Node - 1244/Components/Node - 1482/OSF Storage/OSF Storage/OSF Storage/file.txt'
        '/OSF/Node - 1244/Components/Node - 1482/OSF Storage/OSF Storage/OSF Storage/file.txt'
        ['/OSF/Node - 1244/Components/Node - 1482/', '', '', '/file.txt']
        '/OSF/Node - 1244/Components/Node - 1482/'
        ['Node - 1244', 'Components', 'Node - 1482']
        'Node - 1482'
        1482
    """
    node_id = path.replace(get_current_user().folder, '').split(settings.OSF_STORAGE_FOLDER)[0].strip(os.path.sep).split(os.path.sep)[-1].split(' - ')[-1]
    try:
        with Session() as session:
            return session.query(models.Node).filter(models.Node.id == node_id).one()
    except NoResultFound:
        raise NodeNotFound(path)


def local_to_db(local, node, *, is_folder=False, check_is_folder=True):
    with Session() as session:
        db = session.query(models.File).filter(models.File.parent == None, models.File.node == node).one()  # noqa
    parts = str(local).replace(node.path, '').split(os.path.sep)
    for part in parts:
        for child in db.children:
            if child.name == part:
                db = child
    if db.path.rstrip(os.path.sep) != str(local).rstrip(os.path.sep) or (check_is_folder and db.is_folder != (local.is_dir() or is_folder)):
        return None
    return db


def db_to_remote(db):
    # Fix circular import
    from osfsync.client import osf

    if db.parent is None:
        return _remote_root(db)
    return osf.StorageObject.load(osf.OSFClient().request_session, db.id)


def _remote_root(db):
    # Fix circular import
    from osfsync.client import osf
    return next(
        storage
        for storage in
        osf.NodeStorage.load(osf.OSFClient().request_session, db.node.id)
        if storage.provider == db.provider
    )

def is_ignored(name):
    return IGNORE_RE.match(name) is not None
