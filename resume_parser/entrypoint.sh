#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Create database migrations
echo "Creating database migrations..."
python manage.py makemigrations auth
python manage.py makemigrations parser_app

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate auth
python manage.py migrate parser_app
python manage.py migrate admin
python manage.py migrate

# Create admin user
echo "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='housnijob@gmail.com').exists():
    User.objects.create_user(email='housnijob@gmail.com', name='Keltoum Housni', password='admin', role='ADMIN');
    print('Admin user has been created');
else:
    print('Admin user already exists');
"

# Create superuser for Django admin
echo "Creating superuser for Django admin..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='housnijob@gmail.com').exists():
    User.objects.create_superuser('housnijob@gmail.com', 'admin', 'admin');
    print('Superuser has been created');
else:
    print('Superuser already exists');
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn resume_parser.wsgi:application --bind 0.0.0.0:8000