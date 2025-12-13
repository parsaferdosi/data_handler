#!/bin/bash
cd /app

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Daphne ASGI server..."
daphne -b 0.0.0.0 -p 8000 data_handler.asgi:application