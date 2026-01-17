import os

bind = "0.0.0.0:5000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
accesslog = "-"
errorlog = "-"
