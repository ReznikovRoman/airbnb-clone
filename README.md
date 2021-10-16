# Airbnb Clone

### Technologies:
- Django 3
- Django Channels
- DRF
- Postgres
- Celery
- Redis


## Configuration
Docker containers:
 1. nginx
 2. db
 3. redis
 4. daphne
 5. server
 6. celery
 7. flower
 8. celery_beat

docker-compose files:
 1. `docker-compose-local.yml` - for local development

To run docker containers you have to create a `.env` file in the root directory.

**Example of `.env` file:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=


# Project
ENVIRONMENT=<local,test,prod>
DJANGO_SETTINGS_MODULE=<airbnb.settings.local,airbnb.settings.pro>


# Media & staticfiles
MEDIA_URL=
STATIC_URL=


# Emails
EMAIL_HOST_USER_ESL=<email-username>
EMAIL_HOST_PASSWORD_ESL=<email-password>


# Postgres
POSTGRES_DEFAULT_USER=
POSTGRES_DEFAULT_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=


# Celery
CELERY_BROKER_TRANSPORT=
CELERY_BROKER_HOST=
CELERY_BROKER_PORT=
CELERY_BROKER_VHOST=
CELERY_REDIS_DB=


# Redis
REDIS_URL=${CELERY_BROKER_HOST}://${CELERY_BROKER_TRANSPORT}:${CELERY_BROKER_PORT}/${CELERY_REDIS_DB}
AIRBNB_REDIS_HOST=<airbnb_redis>


# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=


# Sentry
AIRBNB_SENTRY_DSN=


# Flower
CELERY_BROKER_URL=${CELERY_BROKER_HOST}://${CELERY_BROKER_TRANSPORT}:${CELERY_BROKER_PORT}/${CELERY_REDIS_DB}
FLOWER_PORT=

```

**Start project:**

Local:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml up
```

Migrations will be applied automatically.


**Code style:**

Before pushing a commit make sure that your code passes all linters:

```shell
docker-compose -f docker-compose-local.yml run --rm server sh -c "make check"
```

You can also add a `makefile.env` file:
```dotenv
# Your docker-compose file name
DOCKER_COMPOSE_FILENAME=docker-compose-local.yml
```

And then run linters:
```shell
make check-docker
```


**pre-commit:**

To configure pre-commit on your local machine:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml run --rm server "pre-commit install"
```
