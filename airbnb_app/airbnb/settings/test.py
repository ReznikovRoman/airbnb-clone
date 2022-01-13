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
