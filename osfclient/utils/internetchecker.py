import logging
import time

from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


def check_internet():
    try:
        # Use an IP here to avoid block on dns lookup
        urlopen('http://173.194.205.101', timeout=5)
        return True
    except URLError:
        logger.warning('No internet connection')
        return False


def require_internet():
    backoff = 5
    while not check_internet():
        if backoff < 60:
            backoff += 5
        time.sleep(backoff)
