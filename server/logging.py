import logging.config
from django.utils.log import DEFAULT_LOGGING

LOGGING_CONFIG = None

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(funcName)s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
        # application logger
        'metrogas': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
        # root logger
        '': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
    },
}

logging.config.dictConfig(DEFAULT_LOGGING)
