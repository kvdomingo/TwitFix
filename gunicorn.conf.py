wsgi_app = "twitfix.wsgi:app"

worker_class = "uvicorn.workers.UvicornWorker"
workers = 5

pidfile = "/tmp/gunicorn.pid"

errorlog = "-"
accesslog = "-"
loglevel = "debug"
capture_output = True
