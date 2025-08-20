from django.core.management.base import BaseCommand
from airinua.models import Product, Manufacturer

class Command(BaseCommand):
    help = 'Очищає всі товари та виробників з каталогу'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-manufacturers',
            action='store_true',
            help='Залишити виробників, видалити тільки товари',
        )

    def handle(self, *args, **options):
        keep_manufacturers = options['keep_manufacturers']
        
        # Підраховуємо кількість товарів перед видаленням
        products_count = Product.objects.count()
        manufacturers_count = Manufacturer.objects.count()
        
        self.stdout.write(f"🔍 Знайдено товарів: {products_count}")
        self.stdout.write(f"🔍 Знайдено виробників: {manufacturers_count}")
        
        if products_count == 0:
            self.stdout.write(
                self.style.WARNING("ℹ️ Каталог вже порожній. Немає що видаляти.")
            )
            return
        
        # Видаляємо всі товари
        deleted_products = Product.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"✅ Видалено товарів: {deleted_products[0]}")
        )
        
        # Видаляємо виробників, якщо не вказано їх залишити
        if not keep_manufacturers:
            deleted_manufacturers = Manufacturer.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"✅ Видалено виробників: {deleted_manufacturers[0]}")
            )
        else:
            self.stdout.write(
                self.style.WARNING("ℹ️ Виробники залишені (--keep-manufacturers)")
            )
        
        # Перевіряємо результат
        remaining_products = Product.objects.count()
        remaining_manufacturers = Manufacturer.objects.count()
        
        self.stdout.write(f"📊 Залишилося товарів: {remaining_products}")
        self.stdout.write(f"📊 Залишилося виробників: {remaining_manufacturers}")
        
        self.stdout.write(
            self.style.SUCCESS("🎯 Каталог успішно очищено!")
        )
