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

from airinua.models import Product, Manufacturer

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
        
        # Створюємо новий товар
        try:
            product = Product.objects.create(
                name=product_data['name'],
                manufacturer=manufacturer,
                btu=product_data['btu'],
                area_coverage=product_data['area_coverage'],
                price=product_data['price'],
                description=product_data['description'],
                image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop&text=Placeholder',
                is_available=True
            )
            
            created_count += 1
            print(f"✅ Додано товар: {product_data['name']} - {product_data['price']} грн")
            
        except Exception as e:
            print(f"❌ Помилка при створенні товару {product_data['name']}: {str(e)}")
    
    return created_count

def main():
    """Головна функція"""
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
