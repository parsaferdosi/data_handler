import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_handler.settings")

app = Celery("data_handler")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "scan-redis-every-second": {
        "task": "handler.tasks.scan_redis",
        "schedule": 5.0,
    },
}

