#!/bin/bash

set -e

service redis-server start
/etc/init.d/cron start
#gunicorn with ssl
exec gunicorn -c gun.py --certfile=/etc/nginx/server.crt --keyfile=/etc/nginx/server.key app:app
