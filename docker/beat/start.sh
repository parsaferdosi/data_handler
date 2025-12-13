#!/bin/bash
cd /app
celery -A data_handler beat -l info