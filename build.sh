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
                
                # Create comprehensive search variants based on actual file names
                search_variants = []
                
                # Extract key parts from product name
                product_name_clean = name.replace('Кондиціонер ', '').replace(' настінний', '')
                
                # Brand-specific search patterns
                if 'Kaisai' in name:
                    if 'KEX-09KTH2I' in name:
                        search_variants.extend(['Kaisai-KEX-09KTH2I:KEX-09KTH2O-серій-ECO', 'KEX-09KTH2I'])
                    elif 'KEX-12KTH2I' in name:
                        search_variants.extend(['Kaisai-KEX-12KTH2I:KEX-12KTH2O-серій-ECO', 'KEX-12KTH2I'])
                    elif 'KGE-09GRHI' in name:
                        search_variants.extend(['Kaisai-KGE-09GRHI:KGE-09GRHO-серій-GEO', 'KGE-09GRHI'])
                    elif 'KGE-12GRHI' in name:
                        search_variants.extend(['Kaisai-KGE-12GRHI:KGE-12GRHO-серій-GEO', 'KGE-12GRHI'])
                    search_variants.extend(['Kaisai', 'KEX', 'KGE'])
                
                elif 'Gree' in name:
                    if 'GWH07AWAXA' in name:
                        search_variants.extend(['Gree-Cosmo-R-32-GWH07AWAXA-K6DNA1B:I', 'GWH07AWAXA'])
                    elif 'GWH09AWCXB' in name:
                        search_variants.extend(['Gree-Cosmo-R-32-GWH09AWCXB-K6DNA1A:I', 'GWH09AWCXB'])
                    elif 'GWH12AWCXB' in name:
                        search_variants.extend(['Gree-Cosmo-R-32-GWH12AWCXB-K6DNA1A:I', 'GWH12AWCXB'])
                    search_variants.extend(['Gree', 'Cosmo', 'GWH'])
                
                elif 'Olmo' in name:
                    if 'OSH-09HH' in name:
                        search_variants.extend(['Olmo-OSH-09FWH-Серія-Premion-HEAT-PUMP', 'OSH-09HH', 'OSH-09FWH'])
                    elif 'OSH-12HH' in name:
                        search_variants.extend(['Olmo-OSH-12FWH-Серія-Premion-HEAT-PUMP', 'OSH-12HH', 'OSH-12FWH'])
                    search_variants.extend(['Olmo', 'OSH'])
                
                elif 'TCL' in name:
                    if 'TAC-09CHSD' in name and 'FAI' in name:
                        search_variants.extend(['TCL-TAC-09CHSD:FAI-Inverter-R32 WI-FI', 'TAC-09CHSD:FAI'])
                    elif 'TAC-12CHSD' in name and 'FAI' in name:
                        search_variants.extend(['TCL-TAC-12CHSD:FAI-Inverter-R32-WI-FI', 'TAC-12CHSD:FAI'])
                    search_variants.extend(['TCL', 'TAC-09CHSD', 'TAC-12CHSD'])
                
                elif 'AUX' in name:
                    if 'ASW-AS-H09JAR3DI' in name and 'Black' in name:
                        search_variants.extend(['AUX-ASW:AS-H09JAR3DI-J-Smart-Inverter-Black', 'ASW:AS-H09JAR3DI-J-Smart-Inverter-Black'])
                    elif 'ASW-AS-H09JAR3DI' in name:
                        search_variants.extend(['AUX-ASW:AS-H09JAR3DI-Серія-J-Smart-Inverter', 'ASW:AS-H09JAR3DI-Серія-J-Smart-Inverter'])
                    elif 'ASW-AS-H12JAR3DI' in name:
                        search_variants.extend(['AUX-ASW:AS-H12JAR3DI-Серія-J-Smart-Inverter', 'ASW:AS-H12JAR3DI-Серія-J-Smart-Inverter'])
                    search_variants.extend(['AUX', 'ASW:AS-H09JAR3DI', 'ASW:AS-H12JAR3DI'])
                
                elif 'Osaka' in name:
                    if 'STVP-09HH' in name:
                        search_variants.extend(['OSAKA-STVP-09HH-POWER-PRO-DC-INVERTER', 'STVP-09HH'])
                    elif 'STVP-12HH' in name:
                        search_variants.extend(['OSAKA-STVP-12HH-POWER-PRO-DC-INVERTER', 'STVP-12HH'])
                    elif 'STV-09HH' in name:
                        search_variants.extend(['OSAKA-STV-09HH-BASIC-INVERTER', 'STV-09HH'])
                    elif 'STV-12HH' in name:
                        search_variants.extend(['OSAKA-STV-12HH-BASIC-INVERTER', 'STV-12HH'])
                    search_variants.extend(['OSAKA', 'STVP', 'STV'])
                
                elif 'LG' in name:
                    if 'S09EQ' in name:
                        search_variants.extend(['LG-S09EQ', 'S09EQ'])
                    elif 'S12EQ' in name:
                        search_variants.extend(['LG-S12EQ', 'S12EQ'])
                    search_variants.extend(['LG', 'S09EQ', 'S12EQ'])
                
                elif 'Hisense' in name:
                    if 'CF25YR1D' in name:
                        search_variants.extend(['Hisense-CF25YR1D-Omega', 'CF25YR1D'])
                    elif 'CF35YR1D' in name:
                        search_variants.extend(['Hisense-CF35YR1D-Omega', 'CF35YR1D'])
                    search_variants.extend(['Hisense', 'CF25YR1D', 'CF35YR1D'])
                
                elif 'Daikin' in name:
                    if 'FTXA25' in name:
                        search_variants.extend(['Daikin-FTXA25:RXA25A-Stylish', 'FTXA25:RXA25A-Stylish'])
                    elif 'FTXA35' in name:
                        search_variants.extend(['Daikin-FTXA35:RXA35A-Stylish', 'FTXA35:RXA35A-Stylish'])
                    search_variants.extend(['Daikin', 'FTXA25', 'FTXA35'])
                
                # Legacy products search patterns
                elif 'GEO Wind-Free' in name:
                    search_variants.extend(['Samsung-Wind-Free-AR60F09C1BWNUA', 'Wind-Free', 'AR60F09C1BWNUA'])
                elif 'GEO WindFree WI-FI Mass' in name:
                    search_variants.extend(['Samsung-WindFree-WI-FI-Mass-AR12BXFAMWKNUA', 'WindFree-WI-FI-Mass', 'AR12BXFAMWKNUA'])
                elif 'So Cool R-32' in name:
                    search_variants.extend(['Gree-So-Cool', 'So-Cool', 'GWH12APAXF-S6DBA3A'])
                elif 'Vital Plus' in name:
                    search_variants.extend(['Gree-Vital-Plus', 'Vital-Plus', 'CH-S12FTXF6'])
                elif 'Neo' in name:
                    if '09A' in name:
                        search_variants.extend(['CLAIR NEO-09A-R32', 'NEO-09A-R32'])
                    elif '12A' in name:
                        search_variants.extend(['CLAIR NEO-12A-R32', 'NEO-12A-R32'])
                    search_variants.extend(['CLAIR', 'NEO'])
                elif 'Saros' in name:
                    if 'GWH09BBCXD' in name:
                        search_variants.extend(['Gree-Saros-GWH09BBCXD-K6DNA1A:I', 'Saros-GWH09BBCXD'])
                    elif 'GWH12BBCXD' in name:
                        search_variants.extend(['Gree-Saros-GWH12BBCXD-K6DNA1A:I', 'Saros-GWH12BBCXD'])
                    search_variants.extend(['Gree-Saros', 'Saros'])
                elif 'Skylux' in name:
                    if 'SK-09CDR3DI' in name:
                        search_variants.extend(['Skylux-SK-09CDR3DI', 'SK-09CDR3DI'])
                    elif 'SK-12CDR3DI' in name:
                        search_variants.extend(['Skylux-SK-12CDR3DI', 'SK-12CDR3DI'])
                    search_variants.extend(['Skylux', 'SK-09CDR3DI', 'SK-12CDR3DI'])
                
                # Generic fallback patterns
                search_variants.extend([
                    name,
                    product_name_clean,
                    name.replace('Кондиціонер ', ''),
                    name.replace(' настінний', ''),
                    name.replace(' ', '-'),
                    name.replace(' ', '_'),
                    name.replace('/', ':'),
                    name.replace('&', '&')
                ])
                
                # Add manufacturer name
                if manufacturer_name:
                    search_variants.append(manufacturer_name)
                    search_variants.append(manufacturer_name.upper())
                    search_variants.append(manufacturer_name.lower())
                
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

# Additional safety: restore products using our custom command
echo "Running additional product restoration..."
python3 manage.py restore_products

# Force rebuild timestamp
echo "Build completed at: $(date)" > build_timestamp.txt
echo "Products with photos deployed at: $(date)" > products_photos_deploy.txt

# Create superuser if not exists (optional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 