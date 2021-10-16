from .base import *


DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'airbnb-thinknetica.com', 'www.airbnb-thinknetica.com']

ADMINS = (
    ('Roman R', 'esl.manager.mail@gmail.com'),
)


# HTTPS
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_NAME = 'session_airbnb'
SESSION_COOKIE_AGE = 7776000
SESSION_COOKIE_SECURE = True
