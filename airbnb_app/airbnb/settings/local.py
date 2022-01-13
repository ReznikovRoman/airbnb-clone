import mimetypes

from .base import *  # noqa: F401, F403


DEBUG = True

ALLOWED_HOSTS = ['*']

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'airbnb_thinknetica'),
        'USER': os.environ.get('POSTGRES_DEFAULT_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_DEFAULT_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    },
}

# MEDIA
YANDEX_STORAGE_CUSTOM_DOMAIN = None
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / 'airbnb/media/'
RESIZED_MEDIA_URL = '/resized/'

# DEBUG TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda show_toolbar: True,
}
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    'server',
]
mimetypes.add_type('application/javascript', '.js', True)

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} | {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/info.log',  # noqa: F405
            'formatter': 'simple',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/error.log',  # noqa: F405
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'common': {
            'handlers': [
                'file_info',
                'file_error',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
