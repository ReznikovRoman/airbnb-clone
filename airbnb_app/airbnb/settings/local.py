import mimetypes

from .base import *  # noqa: F401, F403


DEBUG = True

ALLOWED_HOSTS = ['*']


# DEBUG TOOLBAR
INTERNAL_IPS = [
    '127.0.0.1',
    '172.18.0.1',
    'localhost',
]
mimetypes.add_type('application/javascript', '.js', True)
