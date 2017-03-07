#! /usr/bin/env python

import sys
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


class SingleInstance:
    """
    Only allow one instance of the program to be run at a time.

    Adapted from tendo library due to python incompatibility
        https://raw.githubusercontent.com/pycontribs/tendo/master/tendo/singleton.py
    """

    def __init__(self, *, flavor_id="", callback=None):
        self.initialized = False
        basename = os.path.splitext(os.path.abspath(sys.argv[0]))[0].replace('/', '-').replace(':', '').replace('\\', '-') + '-%s' % flavor_id + '.lock'
        self.lockfile = os.path.normpath(os.path.join(tempfile.gettempdir(), basename))

        logger.debug("SingleInstance lockfile: " + self.lockfile)
        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous
                # execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError:
                type, e, tb = sys.exc_info()
                if e.errno == 13:
                    logger.error("Another instance is already running, quitting.")
                    if callback:
                        callback()
                    sys.exit(-1)
                raise
        else:  # non Windows
            import fcntl
            self.fp = open(self.lockfile, 'w')
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                logger.warning("Another instance is already running, quitting.")
                if callback:
                    callback()
                sys.exit(-1)
        self.initialized = True

    def __del__(self):
        import sys
        import os
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                import fcntl
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            logger.warning(e)
            sys.exit(-1)
