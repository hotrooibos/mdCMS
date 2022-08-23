import time

"""
GUNICORN configuration file.

"""

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

# Logging
t = time.time()
date = time.strftime('%Y_%m', time.localtime(t))

errorlog = f'logs/{date}_gunicorn_err.log'
loglevel = "info"
accesslog = f'logs/{date}_gunicorn.log'
# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# access_log_format = '%(h)s %(t)s "%(f)s" "%(a)s"'
access_log_format = '%({X-Forwarded-For}i)s %(t)s "%(f)s" "%(a)s"'


"""
Server hooks

"""

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers.")