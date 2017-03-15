import logging

from .defaults import *  # noqa

logger = logging.getLogger(__name__)

try:
    from .local import *  # noqa
except ImportError:
    logger.debug('No local.py found. Using default settings.')


# Define logging configuration to use individual override params from
# settings files
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {'format': FILE_FORMATTER},
        'file_log': {'format': FILE_FORMATTER}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'console'
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'level': LOG_LEVEL
        },
        'logfile': {
            'class': 'logging.FileHandler',
            'level': LOG_LEVEL,
            'filename': PROJECT_LOG_FILE,
            'formatter': 'file_log'
        },
    },
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['console', 'logfile']
    }
}
