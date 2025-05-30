#!/usr/bin/env bash

set -o errexit  # Stop on first error

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗃️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build complete."

 

if [[ $CREATE_SUPERUSER ]];
then
 python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL"
fi

