import mimetypes

from .base import *  # noqa: F401, F403


DEBUG = True

ALLOWED_HOSTS = ['*']


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # noqa: F405
        'NAME': os.environ.get('POSTGRES_DB', 'airbnb_thinknetica'),  # noqa: F405
        'USER': os.environ.get('POSTGRES_DEFAULT_USER', 'postgres'),  # noqa: F405
        'PASSWORD': os.environ.get('POSTGRES_DEFAULT_PASSWORD', 'postgres'),  # noqa: F405
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),  # noqa: F405
        'PORT': os.environ.get('POSTGRES_PORT', 5432),  # noqa: F405
    },
}


# DEBUG TOOLBAR
INTERNAL_IPS = [
    '127.0.0.1',
    '172.18.0.1',
    'localhost',
]
mimetypes.add_type('application/javascript', '.js', True)
