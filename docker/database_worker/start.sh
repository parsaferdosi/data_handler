#!/bin/bash
cd /app
celery -A data_handler worker -Q celery -c 1 --max-tasks-per-child=10 -n db_worker@%h -l info