#!/bin/bash

flask --app main db init
flask --app main db migrate

flask --app main db upgrade

gunicorn --bind 0.0.0.0:10000 main:app