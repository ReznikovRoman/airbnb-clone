#!/bin/bash

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 0.1
    done

    echo "Postgres started"
fi

python manage.py migrate --settings=airbnb.settings.local --noinput
python manage.py collectstatic --settings=airbnb.settings.local --no-input

exec "$@"
