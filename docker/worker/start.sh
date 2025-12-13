#!/bin/bash
cd /app
celery -A data_handler worker -l info
