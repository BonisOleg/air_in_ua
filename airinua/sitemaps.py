from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Product, Service

class StaticViewSitemap(Sitemap):
    """Sitemap для статичних сторінок."""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'airinua:index',
            'airinua:catalog', 
            'airinua:services',
            'airinua:about',
            'airinua:contacts',
            'airinua:portfolio',
            'airinua:faq',
        ]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()

class ServicePagesSitemap(Sitemap):
    """Sitemap для SEO-сторінок послуг."""
    priority = 0.9
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return [
            'airinua:montazh-kondytsioneriv-kyiv',
            'airinua:servis-kondytsioneriv-kyiv', 
            'airinua:chystka-kondytsioneriv-kyiv',
            'airinua:remont-kondytsioneriv-kyiv',
            'airinua:zapravka-kondytsioneriv-kyiv',
        ]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()

class ProductSitemap(Sitemap):
    """Sitemap для товарів."""
    changefreq = 'daily'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Product.objects.filter(is_available=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else timezone.now()

    def location(self, obj):
        # Повертаємо URL товару (потрібно додати у майбутньому)
        return f'/catalog/{obj.id}/'

class ServiceSitemap(Sitemap):
    """Sitemap для послуг."""
    changefreq = 'weekly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Service.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else timezone.now()

    def location(self, obj):
        # Повертаємо URL послуги (потрібно додати у майбутньому)
        return f'/services/{obj.id}/'

# Словник всіх sitemap для використання в urls.py
sitemaps = {
    'static': StaticViewSitemap,
    'services': ServicePagesSitemap,
    'products': ProductSitemap,
    'service_items': ServiceSitemap,
} 