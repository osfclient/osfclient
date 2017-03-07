import os

from appdirs import user_data_dir
from appdirs import user_log_dir

# General settings
PROJECT_NAME = 'osf-sync'
PROJECT_AUTHOR = 'cos'
APPLICATION_SCOPES = 'osf.full_write'

DEBUG = True

DRY = False

# Base URL for API server; used to fetch data
OSF_URL = 'https://test.osf.io'
API_BASE = 'https://test-api.osf.io'
API_VERSION = 'v2'
FILE_BASE = 'https://test-files.osf.io'

# Interval (in seconds) to poll the OSF for server-side file changes
REMOTE_CHECK_INTERVAL = 60 * 5  # Every 5 minutes

#internet checker interval
INTERNET_CHECK_INTERVAL = 60

# Time to keep alert messages on screen (in seconds); may not be configurable on all platforms
ALERT_DURATION = 5.0  # sec

# HTTP request timeouts
CONNECT_TIMEOUT = 7
READ_TIMEOUT = 10

LOG_LEVEL = 'DEBUG'

# sentry configuration. import from local
SENTRY_DSN = None
refs = None

# Logging configuration
FILE_FORMATTER = '[%(levelname)s][%(asctime)s][%(threadName)s][%(name)s]: %(message)s'

IGNORED_PATTERNS = [
    r'\.DS_Store',
    r'lost+found',
    r'Desktop\.ini',
    r'~\$.*',
    r'.*\.tmp',
    r'\..*\.swp',
]

OSF_STORAGE_FOLDER = 'OSF Storage'
COMPONENTS_FOLDER = 'Components'

# Variables used to control where application config data is stored
PROJECT_DB_DIR = user_data_dir(appname=PROJECT_NAME, appauthor=PROJECT_AUTHOR)
PROJECT_DB_FILE = os.path.join(PROJECT_DB_DIR, 'osf.db')

PROJECT_LOG_DIR = user_log_dir(appname=PROJECT_NAME, appauthor=PROJECT_AUTHOR)
PROJECT_LOG_FILE = os.path.join(PROJECT_LOG_DIR, 'osfsync.log')

EVENT_DEBOUNCE = 3

# updater
REPO = 'CenterForOpenScience/OSF-Sync'
VERSION = '0.5.0'
NAME = 'OSF-Sync'
MIN_VERSION_URL = 'https://raw.githubusercontent.com/CenterForOpenScience/OSF-Sync/develop/deploy/version.json'
PROJECT_ON_OSF = 'https://osf.io/v2y6z/files/'
