import os
import gevent.monkey
gevent.monkey.patch_all()

import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import multiprocessing

debug=False
loglevel = 'info'
bind = '0.0.0.0:8001'
pidfile = '../log/gunicorn.pid'
accesslog = "/dev/null"  
errorlog = "/dev/null"    

acclog = logging.getLogger('gunicorn.access')
acclog.addHandler(WatchedFileHandler('../log/gunicorn_access.log'))
acclog.propagate = False
errlog = logging.getLogger('gunicorn.error')
errlog.addHandler(WatchedFileHandler('../log/gunicorn_error.log'))
errlog.propagate = False

workers = multiprocessing.cpu_count() * 2 + 1 
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED-FOR'
