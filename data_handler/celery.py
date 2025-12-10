import os
from celery import Celery
"""
celery application configuration for the data_handler project.
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_handler.settings")

app = Celery("data_handler")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


