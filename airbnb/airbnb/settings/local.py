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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
