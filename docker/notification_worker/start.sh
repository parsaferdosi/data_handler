#!/bin/bash
cd /app
celery -A data_handler worker -Q notify_queue -n notify_worker@%h -l info