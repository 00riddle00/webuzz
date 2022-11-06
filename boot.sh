#!/bin/sh
source venv/bin/activate
flask deploy
exec gunicorn -b :5000 --access-logfile - --error-logfile - social_blogging_app:app