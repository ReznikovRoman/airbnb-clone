from .base import *  # noqa: F401, F403


DEBUG = False

ADMINS = (
    ('Roman R', os.environ.get('PROJECT_ADMIN_EMAIL', 'esl.manager.mail@gmail.com')),  # noqa: F405
)

ALLOWED_HOSTS = os.environ.get('PROJECT_ALLOWED_HOSTS', '').split(',')  # noqa: F405

# TODO: ensure secure connection
