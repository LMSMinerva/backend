#!/usr/bin/env bash
# exit on error
set -o errexit

cd minerva
poetry install

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate