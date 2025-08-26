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
    
    products_data = content.strip().split('\n\n')
    
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
                
                # Create comprehensive search variants
                search_variants = [name]
                
                # Basic variants
                if name.startswith('Кондиціонер '):
                    search_variants.append(name.replace('Кондиціонер ', ''))
                
                # End variants
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
                
                # Character replacements
                search_variants.append(name.replace('/', ':'))
                search_variants.append(name.replace('&', '&'))
                
                # Add variants with different separators
                search_variants.append(name.replace(' ', '-'))
                search_variants.append(name.replace(' ', '_'))
                
                # Add variants with different separators for specific characters
                search_variants.append(name.replace(':', '-'))
                search_variants.append(name.replace(':', ':'))
                search_variants.append(name.replace('/', '-'))
                search_variants.append(name.replace('/', ':'))
                search_variants.append(name.replace('&', '&'))
                
                # Add uppercase variants for specific brands
                if 'Clair' in name:
                    search_variants.append('CLAIR')
                if 'Gree' in name:
                    search_variants.append('GREE')
                if 'Samsung' in name:
                    search_variants.append('Samsung')
                if 'Daikin' in name:
                    search_variants.append('Daikin')
                if 'Hisense' in name:
                    search_variants.append('Hisense')
                if 'Skylux' in name:
                    search_variants.append('Skylux')
                
                # Add variants with common abbreviations
                if 'Supreme Continental silver' in name:
                    search_variants.append(name.replace('Supreme Continental silver', 'Supreme-Continental-silver'))
                    search_variants.append(name.replace('Supreme Continental silver', 'Supreme-Continental-silver'))
                
                if 'On-Off Elite' in name:
                    search_variants.append(name.replace('On-Off Elite', 'On-Off-Elite'))
                
                if 'Winter, Two Stage' in name:
                    search_variants.append(name.replace('Winter, Two Stage', 'Winter-Two-Stage'))
                
                # Add variants for new products
                if 'Sensira' in name:
                    search_variants.append(name.replace('Sensira', 'Sensira'))
                    search_variants.append(name.replace('FTXF', 'FTXF'))
                    search_variants.append(name.replace('RXF', 'RXF'))
                    search_variants.append(name.replace('FTX', 'FTX'))
                    search_variants.append(name.replace('RX', 'RX'))
                    # Add specific model variants
                    if 'FTXF35' in name:
                        search_variants.append('FTXA35:RXA35A-Stylish')
                    if 'FTXF25' in name:
                        search_variants.append('FTXA25:RXA25A-Stylish')
                
                if 'So Cool' in name:
                    search_variants.append(name.replace('So Cool', 'So-Cool'))
                    search_variants.append('GWH12APAXF-S6DBA3A')
                
                if 'Vital Plus' in name:
                    search_variants.append(name.replace('Vital Plus', 'Vital-Plus'))
                    search_variants.append('CH-S12FTXF6')
                
                if 'Inverter R32 WI-FI' in name:
                    search_variants.append(name.replace('Inverter R32 WI-FI', 'Inverter-R32-WI-FI'))
                    search_variants.append('TAC-09CHSD')
                    search_variants.append('TAC-12CHSD')
                
                if 'Wind-Free' in name:
                    search_variants.append(name.replace('Wind-Free', 'Wind-Free'))
                    search_variants.append('AR60F09C1BWNUA')
                
                if 'WindFree WI-FI Mass' in name:
                    search_variants.append(name.replace('WindFree WI-FI Mass', 'WindFree-WI-FI-Mass'))
                    search_variants.append('AR12BXFAMWKNUA')
                
                if 'Neo' in name:
                    search_variants.append(name.replace('Neo', 'Neo'))
                    search_variants.append('Neo 09A')
                    search_variants.append('Neo 12A')
                    # Add specific Clair variants
                    if '09A' in name:
                        search_variants.append('CLAIR NEO-09A-R32')
                    if '12A' in name:
                        search_variants.append('CLAIR NEO-12A-R32')
                
                if 'Saros' in name:
                    search_variants.append(name.replace('Saros', 'Saros'))
                    search_variants.append('GWH09BBCXD-K6DNA1A')
                    search_variants.append('GWH12BBCXD-K6DNA1A')
                    # Add specific Gree Saros variants
                    if 'GWH09BBCXD' in name:
                        search_variants.append('Gree-Saros-GWH09BBCXD-K6DNA1A:I')
                    if 'GWH12BBCXD' in name:
                        search_variants.append('Gree-Saros-GWH12BBCXD-K6DNA1A:I')
                
                if 'Skylux' in name:
                    search_variants.append(name.replace('Skylux', 'Skylux'))
                    search_variants.append('SK-09CDR3DI')
                    search_variants.append('SK-12CDR3DI')
                    # Add specific Skylux variants
                    if 'SK-09CDR3DI' in name:
                        search_variants.append('Skylux-SK-09CDR3DI')
                    if 'SK-12CDR3DI' in name:
                        search_variants.append('Skylux-SK-12CDR3DI')
                
                if 'Omega' in name:
                    search_variants.append(name.replace('Omega', 'Omega'))
                    search_variants.append('CF25YR1D')
                    search_variants.append('CF35YR1D')
                    # Add specific Hisense variants
                    if 'CF25YR1D' in name:
                        search_variants.append('Hisense-CF25YR1D-Omega')
                    if 'CF35YR1D' in name:
                        search_variants.append('Hisense-CF35YR1D-Omega')
                
                # Word-based variants
                words = name.split()
                if len(words) >= 2:
                    search_variants.append(' '.join(words[:2]))
                    if len(words) >= 3:
                        search_variants.append(' '.join(words[:3]))
                
                # Add manufacturer-specific variants
                if 'TCL' in name:
                    search_variants.append('TCL')
                if 'Cooper&Hunter' in name:
                    search_variants.append('Cooper&Hunter')
                if 'GREE' in name:
                    search_variants.append('GREE')
                if 'Hoapp' in name:
                    search_variants.append('Hoapp')
                if 'Daikin' in name:
                    search_variants.append('Daikin')
                if 'Gorenje' in name:
                    search_variants.append('Gorenje')
                if 'TKS' in name:
                    search_variants.append('TKS')
                if 'Samsung' in name:
                    search_variants.append('Samsung')
                if 'Clair' in name:
                    search_variants.append('Clair')
                if 'Skylux' in name:
                    search_variants.append('Skylux')
                if 'Hisense' in name:
                    search_variants.append('Hisense')
                
                # Remove duplicates
                search_variants = list(set(search_variants))
                
                print(f'  🔍 Пошук фото для: {name}')
                print(f'     Варіанти пошуку: {len(search_variants)}')
                
                # Find photos
                photos_found = []
                for photo_file in photo_dir.iterdir():
                    if photo_file.is_file() and photo_file.suffix in ['.webp', '.jpg', '.png']:
                        for variant in search_variants:
                            if variant and variant in photo_file.name:
                                photos_found.append(photo_file)
                                print(f'     ✅ Знайдено: {photo_file.name} (варіант: {variant})')
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
                        
                        print(f'    ✅ Додано фото: {photo_file.name}')
                        
                    except Exception as e:
                        print(f'    ❌ Помилка додавання {photo_file.name}: {e}')
                
                if main_image_url:
                    print(f'  🎯 Встановлено головне фото: {main_image_url}')
                else:
                    print(f'  ⚠️  Для цього товару немає фото')
            
        except Exception as e:
            print(f'❌ Помилка обробки товару: {e}')
            continue

# Run import
import_products_with_photos()
print('🎉 Товари з фото успішно імпортовано!')
"

# Force rebuild timestamp
echo "Build completed at: $(date)" > build_timestamp.txt
echo "Products with photos deployed at: $(date)" > products_photos_deploy.txt

# Create superuser if not exists (optional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 