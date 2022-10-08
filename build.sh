#!/usr/bin/env bash
# exit on error
set -o errexit

# poetry install
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py createsuperuser2 --username LuigiP --password 27597192F --noinput --email 'luigipircio99@gmail.com'