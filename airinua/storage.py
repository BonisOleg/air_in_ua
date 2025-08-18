"""
Cloudinary storage для збереження медіафайлів на Render.
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
import os


@deconstructible
class CloudinaryStorage(Storage):
    """
    Cloudinary storage для Django.
    Зберігає файли в хмарі замість локального диску.
    """
    
    def __init__(self, location=None, base_url=None):
        self.location = location or ''
        self.base_url = base_url
        
        # Ініціалізуємо Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )
    
    def _open(self, name, mode='rb'):
        """Відкриває файл з Cloudinary."""
        try:
            # Отримуємо URL файлу з Cloudinary
            result = cloudinary.api.resource(name)
            if result.get('secure_url'):
                import requests
                response = requests.get(result['secure_url'])
                return ContentFile(response.content, name=name)
        except:
            pass
        return ContentFile(b'', name=name)
    
    def _save(self, name, content):
        """Зберігає файл в Cloudinary."""
        try:
            # Завантажуємо файл в Cloudinary
            result = cloudinary.uploader.upload(
                content,
                public_id=name,
                folder=self.location,
                overwrite=True
            )
            return result['public_id']
        except Exception as e:
            # Якщо помилка - повертаємо оригінальну назву
            return name
    
    def exists(self, name):
        """Перевіряє чи існує файл в Cloudinary."""
        try:
            cloudinary.api.resource(name)
            return True
        except:
            return False
    
    def url(self, name):
        """Повертає URL файлу з Cloudinary."""
        try:
            result = cloudinary.api.resource(name)
            return result.get('secure_url', '')
        except:
            return ''
    
    def delete(self, name):
        """Видаляє файл з Cloudinary."""
        try:
            cloudinary.uploader.destroy(name)
        except:
            pass
    
    def size(self, name):
        """Повертає розмір файлу."""
        try:
            result = cloudinary.api.resource(name)
            return result.get('bytes', 0)
        except:
            return 0
    
    def get_accessed_time(self, name):
        """Повертає час останнього доступу."""
        return None
    
    def get_created_time(self, name):
        """Повертає час створення."""
        try:
            result = cloudinary.api.resource(name)
            return result.get('created_at')
        except:
            return None
    
    def get_modified_time(self, name):
        """Повертає час модифікації."""
        try:
            result = cloudinary.api.resource(name)
            return result.get('updated_at')
        except:
            return None
