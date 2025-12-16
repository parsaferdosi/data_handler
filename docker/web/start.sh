#!/bin/bash
set -e

cd /app

# -------- Migration with retry --------
MAX_RETRIES=5
COUNT=0

echo "Applying database migrations..."

until python manage.py migrate; do
  COUNT=$((COUNT+1))
  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    echo "Migration failed after $MAX_RETRIES attempts."
    exit 1
  fi
  echo "Migration failed. Retrying ($COUNT/$MAX_RETRIES)..."
  sleep 3
done

echo "Migrations applied successfully."

# -------- Create superuser if not exists --------
echo "Ensuring superuser exists..."

python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()
username = "parsa"
password = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

# -------- Collect static files --------
echo "Collecting static files..."
python manage.py collectstatic --noinput

# -------- Start ASGI server --------
echo "Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p 8000 data_handler.asgi:application
