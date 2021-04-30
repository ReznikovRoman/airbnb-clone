#!/bin/bash

killall -9 daphne & wait & killall -9 flower

sudo nginx -s reload

uwsgi --ini prod_config/uwsgi.ini & wait &
daphne -u /tmp/daphne_airbnb.sock airbnb.asgi:application & wait &
celery -A airbnb worker -l info &
flower -A airbnb --port=5555 &
celery -A airbnb beat -l info --pidfile= --scheduler django_celery_beat.schedulers:DatabaseScheduler &
python manage.py migrate --settings=airbnb.settings.pro &
