#!/usr/bin/env bash
# exit on error
set -o errexit

cd minerva
poetry install

poetry run python manage.py collectstatic --no-input
poetry run python manage.py makemigrations
poetry run python manage.py migrate