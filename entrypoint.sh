#!/bin/sh

echo "Waiting for MySQL database..."
while ! nc -z $MYSQL_HOST 3306; do
  sleep 0.5
done
echo "MySQL started!"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn server
exec gunicorn storefront.wsgi:application --bind 0.0.0.0:8000 --workers 3
