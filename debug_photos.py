#!/usr/bin/env python3
"""
Скрипт для діагностики проблем з фото товарів
"""
import os
import sys
import django
import requests
from urllib.parse import urlparse

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from airinua.models import Product

def check_image_url(url):
    """Перевіряє чи доступне зображення за URL"""
    if not url:
        return False, "URL порожній"
    
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                return True, f"OK - {content_type}"
            else:
                return False, f"Не зображення - {content_type}"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Помилка запиту: {str(e)}"

def diagnose_photos():
    """Діагностика всіх фото товарів"""
    print("🔍 ДІАГНОСТИКА ФОТО ТОВАРІВ")
    print("=" * 50)
    
    products = Product.objects.all()
    print(f"Всього товарів: {products.count()}")
    
    for product in products:
        print(f"\n📦 Товар: {product.name} (ID: {product.id})")
        print(f"   URL фото: {product.image_url}")
        
        if product.image_url:
            is_valid, message = check_image_url(product.image_url)
            status = "✅" if is_valid else "❌"
            print(f"   Статус: {status} {message}")
        else:
            print("   Статус: ❌ Немає URL фото")
        
        print(f"   Доступний: {'✅' if product.is_available else '❌'}")

if __name__ == "__main__":
    diagnose_photos()
