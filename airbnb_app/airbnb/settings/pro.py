from .base import *


DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'airbnb-thinknetica.com', 'www.airbnb-thinknetica.com']

ADMINS = (
    ('Roman R', 'esl.manager.mail@gmail.com'),
)


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


# HTTPS
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_NAME = 'session_airbnb'
SESSION_COOKIE_AGE = 7776000
SESSION_COOKIE_SECURE = True
