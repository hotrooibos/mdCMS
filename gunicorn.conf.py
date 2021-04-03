'''
GUNICORN configuration file.

'''

from time import sleep
from mdcms import md, constants
import threading as th 


bind = '127.0.0.1:8000'
backlog = 2048


# Worker processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2


# Server mechanics
daemon = False


#   Logging
errorlog = 'gunicorn_err.log'
loglevel = 'info'
accesslog = 'gunicorn.log'
# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
access_log_format = '%(h)s %(t)s "%(f)s" "%(a)s"'


'''
Server hooks

'''

# mdCMS watchdog loop
def mdcms():
    while True:
        md.watchdog()
        sleep(constants.CHECK_TIME)

# Start mdcms daemon in a separate thread on Gunicorn startup
def on_starting(server):
    wd = th.Thread(target=mdcms)
    wd.daemon = True
    wd.start()


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")