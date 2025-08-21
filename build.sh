#!/usr/bin/env bash
# Exit on error
set -o errexit

# Create logs directory if it doesn't exist
mkdir -p logs

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Add products from data file
python3 parse_and_add_products.py --auto

# Update product slugs to fix URL issues
python3 update_slugs.py

# Force rebuild timestamp
echo "Build completed at: $(date)" > build_timestamp.txt
echo "Modal buttons fix deployed at: $(date)" > modal_fix.txt

# Create superuser if not exists (optional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 