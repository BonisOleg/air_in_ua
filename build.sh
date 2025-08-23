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

# Import products with photos
echo "Importing products with photos..."
python3 -c "
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from airinua.models import Product, Manufacturer, ProductImage

def import_products_with_photos():
    # Read products data file
    with open('products_data.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    products_data = content.split('\n\n')
    
    for product_block in products_data:
        if not product_block.strip():
            continue
            
        lines = product_block.strip().split('\n')
        if len(lines) < 8:
            continue
            
        try:
            name = lines[0].strip()
            manufacturer_name = lines[2].strip()
            btu = lines[4].strip().replace(' BTU', '')
            area = lines[6].strip().replace('до ', '').replace(' м²', '')
            price_str = lines[8].strip().replace(' грн', '').replace(',', '.')
            description = '\n'.join(lines[10:])
            
            price = float(price_str)
            
            # Convert BTU and area
            btu_mapping = {'07': '07', '09': '09', '12': '12', '18': '18', '24': '24', '28': '28', '36': '36'}
            area_mapping = {'20': '20', '25': '25', '27': '35', '35': '35', '50': '50', '60': '60', '70': '80', '100': '100'}
            
            btu = btu_mapping.get(btu, '09')
            area = area_mapping.get(area, '25')
            
            # Get or create manufacturer
            manufacturer, created = Manufacturer.objects.get_or_create(name=manufacturer_name)
            
            # Get or create product
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'manufacturer': manufacturer,
                    'btu': btu,
                    'area_coverage': area,
                    'price': price,
                    'description': description,
                    'is_available': True
                }
            )
            
            if not created:
                # Update existing product
                product.manufacturer = manufacturer
                product.btu = btu
                product.area_coverage = area
                product.price = price
                product.description = description
                product.save()
            
            # Find matching photos
            photo_dir = Path('static/img/product')
            if photo_dir.exists():
                # Remove old photos
                ProductImage.objects.filter(product=product).delete()
                
                # Search variants
                search_variants = [name]
                if name.startswith('Кондиціонер '):
                    search_variants.append(name.replace('Кондиціонер ', ''))
                if name.endswith(' inverter'):
                    search_variants.append(name.replace(' inverter', ''))
                if name.endswith(' On-Off Elite'):
                    search_variants.append(name.replace(' On-Off Elite', ''))
                if name.endswith(' Supreme Continental silver'):
                    search_variants.append(name.replace(' Supreme Continental silver', ''))
                if name.endswith(' Winter, Two Stage'):
                    search_variants.append(name.replace(' Winter, Two Stage', ''))
                if name.endswith(' WI-FI Ready'):
                    search_variants.append(name.replace(' WI-FI Ready', ''))
                if name.endswith(' Inverter R32'):
                    search_variants.append(name.replace(' Inverter R32', ''))
                search_variants.append(name.replace('/', ':'))
                search_variants.append(name.replace('&', '&'))
                
                words = name.split()
                if len(words) >= 2:
                    search_variants.append(' '.join(words[:2]))
                    if len(words) >= 3:
                        search_variants.append(' '.join(words[:3]))
                
                # Find photos
                photos_found = []
                for photo_file in photo_dir.iterdir():
                    if photo_file.is_file() and photo_file.suffix in ['.webp', '.jpg', '.png']:
                        for variant in search_variants:
                            if variant in photo_file.name:
                                photos_found.append(photo_file)
                                break
                
                # Remove duplicates and sort
                photos_found = list(set(photos_found))
                photos_found.sort(key=lambda x: x.name)
                
                # Add photos and set main image_url for product
                main_image_url = None
                for i, photo_file in enumerate(photos_found):
                    try:
                        image_url = f'/static/img/product/{photo_file.name}'
                        
                        # Create ProductImage record
                        product_image = ProductImage.objects.create(
                            product=product,
                            image_url=image_url,
                            alt_text=f'{name} - фото {i+1}'
                        )
                        
                        # Set first photo as main image_url for product
                        if i == 0:
                            main_image_url = image_url
                            product.image_url = image_url
                            product.save()
                        
                        print(f'    Added photo: {photo_file.name}')
                        
                    except Exception as e:
                        print(f'    Error adding photo {photo_file.name}: {e}')
                
                if main_image_url:
                    print(f'  Set main image: {main_image_url}')
                else:
                    print(f'  No photos found for: {name}')
            
        except Exception as e:
            print(f'Error processing product: {e}')
            continue

# Run import
import_products_with_photos()
print('Products with photos imported successfully!')
"

# Force rebuild timestamp
echo "Build completed at: $(date)" > build_timestamp.txt
echo "Products with photos deployed at: $(date)" > products_photos_deploy.txt

# Create superuser if not exists (optional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 