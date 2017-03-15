import re
import os

from .. import settings


IGNORE_RE = re.compile(r'.*{}({})'.format(re.escape(os.path.sep),
                                          '|'.join(settings.IGNORED_PATTERNS)))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]
