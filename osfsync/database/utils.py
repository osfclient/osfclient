import shutil

from osfsync import settings


def save(session, *items_to_save):
    for item in items_to_save:
        session.add(item)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise


def remove_db():
    shutil.rmtree(settings.PROJECT_DB_DIR)
