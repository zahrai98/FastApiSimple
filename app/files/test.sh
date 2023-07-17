#!/bin/bash
virtualenv env
source venv/bin/activate
pip install -r requirement.txt
cd evaluation
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
