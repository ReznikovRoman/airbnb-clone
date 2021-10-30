# Airbnb Clone
Website: https://air-project.xyz

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
 2. `docker-compose-master.yml` - for production

Swarm stack files:
1. `stack-master.yml` - for production

To run docker containers you have to create a `.env` file in the root directory.

**Example of `.env` file:**

```dotenv
ENV=.env


# Python
PYTHONUNBUFFERED=


# Project
ENVIRONMENT=<local|test|prod>
DJANGO_SETTINGS_MODULE=<airbnb.settings.local|airbnb.settings.pro>
PROJECT_ALLOWED_HOSTS=<host1,host2>
PROJECT_ADMIN_EMAIL=<admin@email.com>
PROJECT_FULL_DOMAIN=<http://127.0.0.1>
SITE_DEFAULT_PROTOCOL=<http>


# Yandex Object Storage
USE_S3_BUCKET=<0|1>
YANDEX_STORAGE_BUCKET_NAME=
YANDEX_STORAGE_ACCESS_KEY_ID=
YANDEX_STORAGE_SECRET_ACCESS_KEY=


# Media & staticfiles
MEDIA_URL=
STATIC_URL=


# Emails
EMAIL_HOST_USER_ESL=<email@username>
EMAIL_HOST_PASSWORD_ESL=<email.password>


# Postgres
POSTGRES_DEFAULT_USER=
POSTGRES_DEFAULT_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=<db>
POSTGRES_PORT=


# Celery
CELERY_BROKER_TRANSPORT=
CELERY_BROKER_HOST=<redis>
CELERY_BROKER_PORT=
CELERY_BROKER_VHOST=
CELERY_RESULT_BACKEND=<redis>


# Redis
REDIS_DECODE_RESPONSES=1
REDIS_PORT=6379
REDIS_URL=
AIRBNB_REDIS_HOST=<redis>

# Redis DBs
REDIS_CACHE_DB=
REDIS_MAIN_DB=
REDIS_SESSION_DB=
CELERY_REDIS_DB=
REDIS_CHANNELS_DB=

# Channels
REDIS_CHANNELS_URL=


# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=


# Sentry
AIRBNB_SENTRY_DSN=


# Flower
CELERY_BROKER_URL=
FLOWER_PORT=


# DOCKER HUB / CI - optional
DOCKER_HUB_USERNAME=<dockerhub-username>
DOCKER_HUB_PASSWORD=<dockerhub-password>
CI_COMMIT_SHORT_SHA=<latest>

```

**Start project:**

Local:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml up
```

Production docker-compose:
1. Create ./config/nginx/certs/ folder (in the repository root)
2. Add ssl files:
   - air-project.crt: ssl certificate
   - air-project.key: private key
   - ca.crt: root certificate
3. Run docker containers

```shell
docker-compose -f docker-compose-master.yml build
docker-compose -f docker-compose-master.yml up
```

Production Swarm:
1. Create ./config/nginx/certs/ folder (in the repository root)
2. Add ssl files:
   - air-project.crt: ssl certificate
   - air-project.key: private key
   - ca.crt: root certificate
3. Build and push your image to the Docker Hub
4. Deploy Swarm stack

```shell
env $(cat .env | grep ^[A-Z] | xargs) docker stack deploy -c stack-master.yml airbnb_app --with-registry-auth
```

Migrations will be applied automatically.


**Code style:**

Before pushing a commit run all linters:

```shell
docker-compose -f docker-compose-local.yml run --rm server sh -c "make check"
```

You also have to add a `makefile.env` file (for pre-commit):
```dotenv
# Your docker-compose file name
DOCKER_COMPOSE_FILENAME=<docker-compose-local.yml>
```

And then run linters:
```shell
make check-docker
```


**pre-commit:**

To configure pre-commit on your local machine:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml run --rm server sh -c "pre-commit install"
```
