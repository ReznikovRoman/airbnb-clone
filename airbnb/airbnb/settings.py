import os
from pathlib import Path

from django.urls import reverse_lazy
from django.contrib.messages import constants as messages_constants


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=g(33qw)hiwuk&$nrdwr#=xd2cblmh0&k^*he)-gq^4#a$b6*r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    'bootstrap4',
    'debug_toolbar',
    'django_inlinecss',
    'ckeditor',
    'ckeditor_uploader',
    'sorl.thumbnail',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'accounts.apps.AccountsConfig',
    'main.apps.MainConfig',
    'addresses.apps.AddressesConfig',
    'hosts.apps.HostsConfig',
    'realty.apps.RealtyConfig',

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
]

ROOT_URLCONF = 'airbnb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'realty/templates',
            BASE_DIR / 'hosts/templates',

            BASE_DIR / 'templates/allauth',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'airbnb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# SITES
SITE_ID = 1


# DEBUG TOOLBAR
if DEBUG:
    import mimetypes
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    mimetypes.add_type('application/javascript', '.js', True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/'


# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'


# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER_ESL')
DEFAULT_FROM_EMAIL = 'support@airbnb.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD_ESL')


# LOGIN
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = reverse_lazy('account_login')
LOGIN_REDIRECT_URL = reverse_lazy('home_page')


# MESSAGES
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'alert-secondary',
    messages_constants.INFO: 'alert-info',
    messages_constants.SUCCESS: 'alert-success',
    messages_constants.WARNING: 'alert-warning',
    messages_constants.ERROR: 'alert-danger',
}


# ALLAUTH
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('AIRBNB_GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('AIRBNB_GOOGLE_CLIENT_SECRET'),
            'key': '',
        },
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
    }
}
SOCIALACCOUNT_QUERY_EMAIL = True


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
                'Maximize',
            ]},
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
    }
}
