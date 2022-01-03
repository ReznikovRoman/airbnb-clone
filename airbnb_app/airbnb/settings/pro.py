import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F401, F403


DEBUG = False

ALLOWED_HOSTS = os.environ.get('PROJECT_ALLOWED_HOSTS', '').split(',')

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_YANDEX_DB'),
        'USER': os.environ.get('POSTGRES_YANDEX_USER'),
        'PASSWORD': os.environ.get('POSTGRES_YANDEX_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_YANDEX_HOST'),
        'PORT': os.environ.get('POSTGRES_YANDEX_PORT'),
        'OPTIONS': {
            'target_session_attrs': 'read-write',
            'sslmode': 'verify-full',
            'sslrootcert': os.environ.get('POSTGRES_SSL_CERT_DOCKER_PATH'),
        },
    },
}

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'main.middleware.MobileUserAgentMiddleware',
]

# STATIC
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# MEDIA
if USE_S3_BUCKET:
    # Yandex Object Storage settings
    YANDEX_STORAGE_CUSTOM_DOMAIN = f'{YANDEX_STORAGE_BUCKET_NAME}.storage.yandexcloud.net'
    DEFAULT_FILE_STORAGE = 'storage_backends.YandexObjectMediaStorage'
    AWS_ACCESS_KEY_ID = os.environ.get('YANDEX_STORAGE_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('YANDEX_STORAGE_SECRET_ACCESS_KEY')
    AWS_S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'
    AWS_S3_REGION_NAME = 'ru-central1'

    # Media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{YANDEX_STORAGE_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
else:
    # MEDIA
    MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
    MEDIA_ROOT = BASE_DIR / 'airbnb/media/'


# REDIS
REDIS_SSL_CERT_DOCKER_PATH = os.environ.get("REDIS_SSL_CERT_DOCKER_PATH")
REDIS_SENTINEL_HOSTS = os.environ.get("REDIS_SENTINEL_HOSTS").split(",")
REDIS_CLUSTER_SENTINELS = [
    (host, 26379) for host in REDIS_SENTINEL_HOSTS
]
REDIS_CLUSTER_NAME = os.environ.get("REDIS_CLUSTER_NAME")
REDIS_CLUSTER_PASSWORD = os.environ.get("REDIS_CLUSTER_PASSWORD")
REDIS_DECODE_RESPONSES = True


# SENTRY
SENTRY_CONF = sentry_sdk.init(
    dsn=os.environ.get("AIRBNB_SENTRY_DSN"),
    integrations=[
        DjangoIntegration(),
        RedisIntegration(),
        CeleryIntegration(),
    ],
)
