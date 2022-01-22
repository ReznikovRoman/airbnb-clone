import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F401, F403


DEBUG = False

ALLOWED_HOSTS = os.environ.get('PROJECT_ALLOWED_HOSTS', '').split(',')

# DATABASE
DATABASE_OPTIONS = {
    'target_session_attrs': 'read-write',
    'sslmode': 'verify-full',
    'sslrootcert': os.environ.get('POSTGRES_SSL_CERT_DOCKER_PATH'),
}
if PROJECT_ENVIRONMENT == "ci":
    DATABASE_OPTIONS = {
        'target_session_attrs': 'read-write',
    }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_YANDEX_DB'),
        'USER': os.environ.get('POSTGRES_YANDEX_USER'),
        'PASSWORD': os.environ.get('POSTGRES_YANDEX_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_YANDEX_HOST'),
        'PORT': os.environ.get('POSTGRES_YANDEX_PORT'),
        'OPTIONS': DATABASE_OPTIONS,
    },
}

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'main.middleware.MobileUserAgentMiddleware',
]


# MEDIA
if USE_S3_BUCKET:
    # Yandex Object Storage settings
    YANDEX_STORAGE_CUSTOM_DOMAIN = os.environ.get("YANDEX_STORAGE_CUSTOM_DOMAIN")
    DEFAULT_FILE_STORAGE = 'storage_backends.YandexObjectMediaStorage'
    AWS_S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'
    AWS_S3_REGION_NAME = 'ru-central1'

    # Media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    PUBLIC_MEDIA_RESIZED_LOCATION = 'resized'
    MEDIA_URL = f'https://{YANDEX_STORAGE_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    RESIZED_MEDIA_URL = f'https://{YANDEX_STORAGE_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_RESIZED_LOCATION}/'
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
REDIS_CLUSTER_SENTINELS_STRING = ",".join(f"{host}:26379" for host in REDIS_SENTINEL_HOSTS)
REDIS_CLUSTER_NAME = os.environ.get("REDIS_CLUSTER_NAME")
REDIS_CLUSTER_PASSWORD = os.environ.get("REDIS_CLUSTER_PASSWORD")
REDIS_DECODE_RESPONSES = True


# CACHES
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"{REDIS_CLUSTER_NAME}/{REDIS_CLUSTER_SENTINELS_STRING}/{REDIS_CACHE_DB}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_sentinel.sentinel.SentinelClient',
            'PASSWORD': REDIS_CLUSTER_PASSWORD,
            'USE_SSL': True,
            'SSL_CA_CERT': REDIS_SSL_CERT_DOCKER_PATH,
        },
    },
}


# SESSIONS
SESSION_REDIS = {
    'db': REDIS_SESSION_DB,
    'password': REDIS_CLUSTER_PASSWORD,
    'prefix': 'session',
    'socket_timeout': 0.5,
    'retry_on_timeout': False,
}
SESSION_REDIS_CONNECTION_OBJECT = None
SESSION_REDIS_SENTINEL_LIST = [
    (host, 26379) for host in REDIS_SENTINEL_HOSTS
]
SESSION_REDIS_SENTINEL_MASTER_ALIAS = REDIS_CLUSTER_NAME
SESSION_REDIS_DB = REDIS_SESSION_DB
SESSION_REDIS_PASSWORD = REDIS_CLUSTER_PASSWORD
SESSION_REDIS_USE_SSL = True
SESSION_REDIS_SSL_CA_CERT_PATH = REDIS_SSL_CERT_DOCKER_PATH


# SENTRY
SENTRY_CONF = sentry_sdk.init(
    dsn=os.environ.get("AIRBNB_SENTRY_DSN"),
    integrations=[
        DjangoIntegration(),
        RedisIntegration(),
        CeleryIntegration(),
    ],
)
