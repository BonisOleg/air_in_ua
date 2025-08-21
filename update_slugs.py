#!/usr/bin/env python3
"""
Скрипт для оновлення slug існуючих товарів
"""
import os
import sys
import django
from django.utils.text import slugify

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from airinua.models import Product

def update_product_slugs():
    """Оновлює slug для всіх існуючих товарів"""
    products = Product.objects.all()
    updated_count = 0
    
    print("🔄 Оновлення slug для товарів...")
    
    for product in products:
        old_slug = product.slug
        # Генеруємо новий slug тільки з назви товару
        new_slug = slugify(product.name)
        
        # Перевіряємо унікальність
        counter = 1
        while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
            new_slug = f"{slugify(product.name)}-{counter}"
            counter += 1
        
        if old_slug != new_slug:
            product.slug = new_slug
            product.save(update_fields=['slug'])
            print(f"✅ Оновлено: {product.name}")
            print(f"   Старий slug: {old_slug}")
            print(f"   Новий slug: {new_slug}")
            updated_count += 1
        else:
            print(f"ℹ️ Без змін: {product.name} ({old_slug})")
    
    print(f"\n🎉 Готово! Оновлено {updated_count} товарів.")
    print(f"📊 Всього товарів: {products.count()}")

if __name__ == "__main__":
    update_product_slugs()
