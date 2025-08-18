"""
Django management команда для створення необхідних медіа директорій.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Створює необхідні директорії для медіафайлів'

    def handle(self, *args, **options):
        """Створює всі необхідні папки для медіафайлів."""
        
        # Список необхідних директорій
        media_dirs = [
            'products',
            'products/gallery', 
            'services',
        ]
        
        # Створюємо MEDIA_ROOT якщо не існує
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Створено MEDIA_ROOT: {settings.MEDIA_ROOT}')
            )
        
        # Створюємо кожну папку
        created_dirs = []
        for dir_name in media_dirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, dir_name)
            
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Створено папку: media/{dir_name}/')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Папка вже існує: media/{dir_name}/')
                )
        
        # Створюємо .gitkeep файли для збереження структури в Git
        for dir_name in media_dirs:
            gitkeep_path = os.path.join(settings.MEDIA_ROOT, dir_name, '.gitkeep')
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    f.write('# Цей файл зберігає структуру папок в Git\n')
                self.stdout.write(
                    self.style.SUCCESS(f'📁 Створено .gitkeep: media/{dir_name}/.gitkeep')
                )
        
        if created_dirs:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Успішно створено {len(created_dirs)} нових папок для медіафайлів!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Всі необхідні папки вже існують!')
            )
        
        # Перевіряємо права доступу
        try:
            test_file = os.path.join(settings.MEDIA_ROOT, 'products', '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            self.stdout.write(
                self.style.SUCCESS('✅ Права на запис у media/products/ - OK')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Помилка прав доступу: {e}')
            )
