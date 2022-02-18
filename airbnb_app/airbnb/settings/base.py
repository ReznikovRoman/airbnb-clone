import os
from datetime import timedelta
from pathlib import Path
from typing import List

from kombu import Exchange, Queue

from django.contrib.messages import constants as messages_constants
from django.urls import reverse_lazy


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=g(33qw)hiwuk&$nrdwr#=xd2cblmh0&k^*he)-gq^4#a$b6*r'


ALLOWED_HOSTS: List[str] = []


# Application definition
INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.postgres',

    # drf
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # django 3rd party
    'bootstrap4',
    'debug_toolbar',
    'django_extensions',
    'django_filters',
    'django_inlinecss',
    'django_celery_beat',
    'ckeditor',
    'ckeditor_uploader',
    'channels',
    'phonenumber_field',
    'sorl.thumbnail',
    'storages',

    # local
    'main.apps.MainConfig',
    'accounts.apps.AccountsConfig',
    'addresses.apps.AddressesConfig',
    'hosts.apps.HostsConfig',
    'realty.apps.RealtyConfig',
    'subscribers.apps.SubscribersConfig',
    'mailings.apps.MailingsConfig',
    'chat_bot.apps.ChatBotConfig',

    # cleanup
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'main.middleware.MobileUserAgentMiddleware',
]

ROOT_URLCONF = 'airbnb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'main/templates',
            BASE_DIR / 'accounts/templates',
            BASE_DIR / 'realty/templates',
            BASE_DIR / 'hosts/templates',
            BASE_DIR / 'subscribers/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'main.context_processors.absolute_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'airbnb.wsgi.application'


# DATABASE
USE_MANAGED_POSTGRES = bool(os.environ.get("USE_MANAGED_POSTGRES", False))


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# AUTHENTICATION
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('home_page')
LOGOUT_REDIRECT_URL = reverse_lazy('home_page')


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# SITES
SITE_ID = 1
DEFAULT_PROTOCOL = os.environ.get("SITE_DEFAULT_PROTOCOL", "http")
PROJECT_FULL_DOMAIN = os.environ.get("PROJECT_FULL_DOMAIN", "http://localhost:8000")


# AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Static files (CSS, JavaScript, Images)
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = BASE_DIR / 'airbnb/static/'


# Message Queue [AWS SQS Api compatible]
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")


# S3 Bucket
USE_S3_BUCKET = bool(int(os.environ.get("USE_S3_BUCKET", 0)))
YANDEX_STORAGE_BUCKET_NAME = os.environ.get("YANDEX_STORAGE_BUCKET_NAME")


# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER_ESL')
DEFAULT_FROM_EMAIL = 'support@airbnb.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD_ESL')


# CHARSET
DEFAULT_CHARSET = "utf-8"


# MESSAGES
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'alert-secondary',
    messages_constants.INFO: 'alert-info',
    messages_constants.SUCCESS: 'alert-success',
    messages_constants.WARNING: 'alert-warning',
    messages_constants.ERROR: 'alert-danger',
}


# PROJECT
PROJECT_ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "prod")


# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
}


# SIMPLE JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# REDIS
REDIS_HOST = os.environ.get('AIRBNB_REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_DB = os.environ.get('REDIS_MAIN_DB', 1)
REDIS_DECODE_RESPONSES = os.environ.get('REDIS_DECODE_RESPONSES', True)


# CACHES
REDIS_CACHE_DB = os.environ.get('REDIS_CACHE_DB', 2)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}


# SESSIONS
REDIS_SESSION_DB = os.environ.get('REDIS_SESSION_DB', 3)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_SESSION_DB,
    'prefix': 'session',
    'socket_timeout': 1,
    'retry_on_timeout': False,
}


# CELERY
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 10 * 60
CELERY_TASK_TIME_LIMIT = 8 * 60 * 60  # 8 hours
CELERY_TASK_SOFT_TIME_LIMIT = 10 * 60 * 60  # 10 hours
CELERY_QUEUES = (
    Queue(name='default', exchange=Exchange('default'), routing_key='default'),
    Queue(name='celery'),
    Queue(name='emails'),
    Queue(name='urgent_notifications'),
)
CELERY_CREATE_MISSING_QUEUES = True
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

# Message Queue
YMQ_ENDPOINT = os.environ.get("YMQ_ENDPOINT", None)
if YMQ_ENDPOINT is not None:
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "visibility_timeout": 12 * 60 * 60,
        "max_retries": 10,
        "is_secure": True,
        "region": AWS_DEFAULT_REGION,
        'predefined_queues': {
            'default': {
                'url': os.environ.get('YMQ_DEFAULT_QUEUE_URL'),
                'access_key_id': AWS_ACCESS_KEY_ID,
                'secret_access_key': AWS_SECRET_ACCESS_KEY,
            },
            'celery': {
                'url': os.environ.get('YMQ_CELERY_QUEUE_URL'),
                'access_key_id': AWS_ACCESS_KEY_ID,
                'secret_access_key': AWS_SECRET_ACCESS_KEY,
            },
            'emails': {
                'url': os.environ.get('YMQ_EMAILS_QUEUE_URL'),
                'access_key_id': AWS_ACCESS_KEY_ID,
                'secret_access_key': AWS_SECRET_ACCESS_KEY,
            },
            'urgent_notifications': {
                'url': os.environ.get('YMQ_URGENT_NOTIFICATIONS_QUEUE_URL'),
                'access_key_id': AWS_ACCESS_KEY_ID,
                'secret_access_key': AWS_SECRET_ACCESS_KEY,
            },
        },
    }
    CELERY_BROKER_URL = f"sqs://{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}@{YMQ_ENDPOINT}"
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
        "visibility_timeout": 60 * 60,
        "retry_policy": {
            "timeout": 5.0,
        },
    }
    CELERY_WORKER_ENABLE_REMOTE_CONTROL = False
else:
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")


# CHANNELS
REDIS_CHANNELS_DB = os.environ.get("REDIS_CHANNELS_DB", 5)
REDIS_CHANNELS_URL = os.environ.get("REDIS_CHANNELS_URL", f"redis://localhost:6379/{REDIS_CHANNELS_DB}")
ASGI_APPLICATION = 'airbnb.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_CHANNELS_URL],
        },
    },
}


# TWILIO
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')


# PHONENUMBER
PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'RU'


# CKEDITOR
CKEDITOR_UPLOAD_PATH = 'upload/images_admin/'
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        'width': 'auto',
        'height': '550px',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor', 'Youtube']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                'Preview',
                'Maximize']
             },
        ],
        'toolbar': '',  # selected toolbar config
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            # extra plugins
            'uploadimage',  # the upload image feature
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
        ]),
    },
}
