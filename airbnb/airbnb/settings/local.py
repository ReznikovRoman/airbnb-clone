import mimetypes

from .base import *


DEBUG = True


# DEBUG TOOLBAR
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]
mimetypes.add_type('application/javascript', '.js', True)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'airbnb_thinknetica'),
        'USER': os.environ.get('POSTGRES_DEFAULT_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_DEFAULT_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}
