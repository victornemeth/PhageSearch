#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn mysite.wsgi:application --bin 0.0.0.0:8000
