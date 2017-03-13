#!/bin/bash

set -e

service redis-server start
/etc/init.d/cron start
exec gunicorn -c gun.py app:app
