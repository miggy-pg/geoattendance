#!/bin/bash
# SUPERUSER_IDNUMBER=${DJANGO_SUPERUSER_IDNUMBER:-"2018-0000"}
# SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"admin"}

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py createsuperuser \
    --user_idnumber ${SUPERUSER_IDNUMBER} --noinput || true