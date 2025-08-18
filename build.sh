#!/usr/bin/env bash
# Exit on error
set -o errexit

# Create logs directory if it doesn't exist
mkdir -p logs

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Create media directories for file uploads
python manage.py create_media_dirs

python manage.py migrate

# Створюємо послуги після міграції
python manage.py populate_services 