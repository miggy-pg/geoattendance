#!/bin/sh

APP_PORT=${PORT:-8000}
cd /app/
gunicorn captiveportal.wsgi:application --bind "0.0.0.0:${APP_PORT}"