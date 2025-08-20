#!/usr/bin/env python3
"""
Скрипт для парсингу файлу з даними товарів та додавання їх до бази даних
"""
import os
import sys
import django
import re

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from airinua.models import Product, Manufacturer, ProductImage

def parse_products_file(filename):
    """Парсить файл з даними товарів"""
    products = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"❌ Файл {filename} не знайдено!")
        return products
    
    # Розділяємо на окремі товари (розділені порожніми рядками)
    product_blocks = content.strip().split('\n\n')
    
    for block in product_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
        
        # Перший рядок - назва товару
        name = lines[0].strip()
        
        # Парсимо інші поля
        product_data = {'name': name}
        
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            
            if line == 'Виробник:':
                if i + 1 < len(lines):
                    product_data['manufacturer'] = lines[i + 1].strip()
                    i += 2
                else:
                    i += 1
            elif line == 'Потужність:':
                if i + 1 < len(lines):
                    btu = lines[i + 1].strip()
                    # Видаляємо "BTU" та пробіли
                    btu_clean = btu.replace('BTU', '').strip()
                    product_data['btu'] = btu_clean
                    i += 2
                else:
                    i += 1
            elif line == 'Площа охолодження:':
                if i + 1 < len(lines):
                    area = lines[i + 1].strip()
                    # Видаляємо "до" та "м²", залишаємо тільки число
                    area_clean = re.sub(r'до\s*(\d+)\s*м²', r'\1', area)
                    product_data['area_coverage'] = area_clean
                    i += 2
                else:
                    i += 1
            elif line == 'Ціна:':
                if i + 1 < len(lines):
                    price_str = lines[i + 1].strip()
                    # Видаляємо "грн", замінюємо кому на крапку, конвертуємо в число
                    price_clean = price_str.replace('грн', '').replace(',', '.').strip()
                    try:
                        product_data['price'] = float(price_clean)
                    except ValueError:
                        print(f"⚠️ Неправильний формат ціни для {name}: {price_str}")
                        product_data['price'] = 0.0
                    i += 2
                else:
                    i += 1
            elif line == 'Опис:':
                # Збираємо весь опис до кінця блоку
                description_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    description_lines.append(lines[i].strip())
                    i += 1
                product_data['description'] = ' '.join(description_lines)
            else:
                i += 1
        
        # Перевіряємо, чи є всі необхідні поля
        required_fields = ['name', 'manufacturer', 'btu', 'area_coverage', 'price', 'description']
        if all(field in product_data for field in required_fields):
            products.append(product_data)
        else:
            print(f"⚠️ Неповні дані для товару: {name}")
            print(f"   Наявні поля: {list(product_data.keys())}")
    
    return products

def find_product_images(product_name):
    """Знаходить зображення для товару в папці static/img/product/"""
    import os
    import glob
    
    # Очищаємо назву товару для пошуку файлів
    # Замінюємо проблемні символи
    clean_name = product_name.replace('/', '_').replace(':', '_')
    
    # Шляхи для пошуку
    search_patterns = [
        f"static/img/product/{clean_name}*.webp",
        f"static/img/product/{clean_name}*.jpg", 
        f"static/img/product/{clean_name}*.png",
        f"static/img/product/{clean_name}*.jpeg"
    ]
    
    images = []
    for pattern in search_patterns:
        found_files = glob.glob(pattern)
        images.extend(found_files)
    
    # Сортуємо за назвою (щоб (1) було першим)
    images.sort()
    
    return images

def add_products_to_database(products):
    """Додає товари до бази даних"""
    created_count = 0
    
    for product_data in products:
        # Створюємо або отримуємо виробника
        manufacturer, created = Manufacturer.objects.get_or_create(
            name=product_data['manufacturer']
        )
        
        # Перевіряємо, чи товар вже існує
        existing_product = Product.objects.filter(
            name=product_data['name'],
            manufacturer=manufacturer
        ).first()
        
        if existing_product:
            print(f"ℹ️ Товар вже існує: {product_data['name']}")
            continue
        
        # Шукаємо зображення для товару
        product_images = find_product_images(product_data['name'])
        
        if product_images:
            # Використовуємо перше зображення як основне
            main_image = product_images[0]
            image_url = f"/static/{main_image.replace('static/', '')}"
            print(f"📸 Знайдено зображення для {product_data['name']}: {main_image}")
        else:
            # Якщо зображення не знайдено, використовуємо placeholder
            image_url = '/static/img/placeholder.png'
            print(f"⚠️ Зображення не знайдено для {product_data['name']}, використовую placeholder")
        
        # Створюємо новий товар
        try:
            product = Product.objects.create(
                name=product_data['name'],
                manufacturer=manufacturer,
                btu=product_data['btu'],
                area_coverage=product_data['area_coverage'],
                price=product_data['price'],
                description=product_data['description'],
                image_url=image_url,
                is_available=True
            )
            
            # Додаємо додаткові зображення як ProductImage
            for i, image_path in enumerate(product_images[1:], 2):  # Починаємо з 2-го зображення
                try:
                    ProductImage.objects.create(
                        product=product,
                        image_url=f"/static/{image_path.replace('static/', '')}"
                    )
                    print(f"  📸 Додано додаткове зображення {i}: {image_path}")
                except Exception as e:
                    print(f"  ⚠️ Помилка додавання зображення {image_path}: {str(e)}")
            
            created_count += 1
            print(f"✅ Додано товар: {product_data['name']} - {product_data['price']} грн")
            
        except Exception as e:
            print(f"❌ Помилка при створенні товару {product_data['name']}: {str(e)}")
    
    return created_count

def main():
    """Головна функція"""
    import sys
    
    # Перевіряємо аргументи командного рядка
    auto_mode = '--auto' in sys.argv
    
    print("🚀 ПАРСИНГ ТА ДОДАВАННЯ ТОВАРІВ")
    print("=" * 50)
    
    # Парсимо файл
    products = parse_products_file('products_data.txt')
    
    if not products:
        print("❌ Не знайдено товарів для додавання!")
        return
    
    print(f"📋 Знайдено товарів у файлі: {len(products)}")
    
    # Показуємо знайдені товари
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Виробник: {product['manufacturer']}")
        print(f"   Потужність: {product['btu']} BTU")
        print(f"   Площа: {product['area_coverage']} м²")
        print(f"   Ціна: {product['price']} грн")
        print(f"   Опис: {product['description'][:100]}...")
    
    # Якщо автоматичний режим - додаємо без підтвердження
    if auto_mode:
        print(f"\n🤖 АВТОМАТИЧНИЙ РЕЖИМ: Додаю {len(products)} товарів...")
    else:
        # Питаємо підтвердження
        response = input(f"\n🤔 Додати {len(products)} товарів до бази даних? (y/n): ")
        
        if response.lower() not in ['y', 'yes', 'так', 'д']:
            print("❌ Операцію скасовано.")
            return
    
    # Додаємо товари
    created_count = add_products_to_database(products)
    
    print(f"\n✅ ГОТОВО! Додано {created_count} нових товарів.")
    print(f"📊 Всього товарів у базі: {Product.objects.count()}")

if __name__ == "__main__":
    main()
