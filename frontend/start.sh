#!/bin/bash


# Start nginx using the default configuration
service nginx start > /dev/null


/usr/bin/python3 ./frontend/manage.py migrate
/usr/bin/python3 ./frontend/manage.py loaddata fields.json

/usr/bin/python3 ./downloader.py &
/usr/bin/python3 ./frontend/manage.py runserver 0.0.0.0:${WEB_PORT:-8000}
