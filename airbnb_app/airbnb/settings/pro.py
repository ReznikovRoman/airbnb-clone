from .base import *  # noqa: F401, F403


DEBUG = False

ALLOWED_HOSTS = os.environ.get('PROJECT_ALLOWED_HOSTS', '').split(',')  # noqa: F405

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # noqa: F405
        'NAME': os.environ.get('POSTGRES_PROD_DB', 'airbnb_thinknetica'),  # noqa: F405
        'USER': os.environ.get('POSTGRES_PROD_USER', 'postgres'),  # noqa: F405
        'PASSWORD': os.environ.get('POSTGRES_PROD_PASSWORD', 'postgres'),  # noqa: F405
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),  # noqa: F405
        'PORT': os.environ.get('POSTGRES_PORT', 5432),  # noqa: F405
    },
}

# HTTPS
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_NAME = 'session_airbnb'
SESSION_COOKIE_AGE = 7776000
SESSION_COOKIE_SECURE = True
