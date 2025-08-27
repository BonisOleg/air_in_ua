from django.core.management.base import BaseCommand
from airinua.models import Product, Manufacturer, ProductImage

class Command(BaseCommand):
    help = 'Відновлює товари після деплою на Render'

    def handle(self, *args, **options):
        self.stdout.write("=== ВІДНОВЛЕННЯ ТОВАРІВ ПІСЛЯ ДЕПЛОЮ ===\n")
        
        # Дані товарів для відновлення
        products_to_restore = [
            # Hisense
            {
                'name': 'Кондиціонер Hisense CF25YR1D Omega',
                'manufacturer_name': 'Hisense',
                'price': 14999.00,
                'btu': '09',
                'area_coverage': '25',
                'description': 'Інверторна спліт-система серії Omega з високим класом енергоефективності A++ та інноваційними функціями. Має режим "I FEEL" для точного контролю температури та низький рівень шуму.',
                'images': [
                    'img/product/Hisense-CF25YR1D-Omega(1).png',
                    'img/product/Hisense-CF25YR1D-Omega(2).png',
                    'img/product/Hisense-CF25YR1D-Omega(3).png',
                    'img/product/Hisense-CF25YR1D-Omega(4).png'
                ]
            },
            {
                'name': 'Кондиціонер Hisense CF35YR1D Omega',
                'manufacturer_name': 'Hisense',
                'price': 16699.00,
                'btu': '12',
                'area_coverage': '35',
                'description': 'Це інверторна спліт-система з високим класом енергоефективності A++ та інноваційними функціями, як-от "I FEEL", завдяки якому температура підтримується відповідно до розташування пульта. Кондиціонер має режим "Super" для швидкого охолодження та низький рівень шуму.',
                'images': [
                    'img/product/Hisense-CF35YR1D-Omega(1).png',
                    'img/product/Hisense-CF35YR1D-Omega(2).png',
                    'img/product/Hisense-CF35YR1D-Omega(3).png',
                    'img/product/Hisense-CF35YR1D-Omega(4).png'
                ]
            },
            # Daikin
            {
                'name': 'Кондиціонер Daikin FTXA25/RXA25A Stylish',
                'manufacturer_name': 'Daikin',
                'price': 28999.00,
                'btu': '09',
                'area_coverage': '25',
                'description': 'Стильна інверторна спліт-система серії Stylish з елегантним дизайном та високою енергоефективністю A++. Має функцію "I FEEL" та технологію "Flash Streamer".',
                'images': [
                    'img/product/Daikin-FTXA25:RXA25A-Stylish(1).png',
                    'img/product/Daikin-FTXA25:RXA25A-Stylish(2).png',
                    'img/product/Daikin-FTXA25:RXA25A-Stylish(3).png',
                    'img/product/Daikin-FTXA25:RXA25A-Stylish(4).png'
                ]
            },
            {
                'name': 'Кондиціонер Daikin FTXA35/RXA35A Stylish',
                'manufacturer_name': 'Daikin',
                'price': 32999.00,
                'btu': '12',
                'area_coverage': '35',
                'description': 'Потужна інверторна спліт-система серії Stylish для великих приміщень. Має високу енергоефективність A++, функцію "I FEEL" та технологію "Flash Streamer".',
                'images': [
                    'img/product/Daikin-FTXA35:RXA35A-Stylish(1).png',
                    'img/product/Daikin-FTXA35:RXA35A-Stylish(2).png',
                    'img/product/Daikin-FTXA35:RXA35A-Stylish(3).png',
                    'img/product/Daikin-FTXA35:RXA35A-Stylish(4).png'
                ]
            }
        ]
        
        restored_count = 0
        
        for product_data in products_to_restore:
            try:
                # Отримуємо або створюємо виробника
                manufacturer, created = Manufacturer.objects.get_or_create(
                    name=product_data['manufacturer_name']
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Створено виробника: {manufacturer.name}")
                    )
                
                # Перевіряємо, чи товар вже існує
                existing_product = Product.objects.filter(name=product_data['name']).first()
                if existing_product:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Товар вже існує: {existing_product.name}")
                    )
                    continue
                
                # Створюємо товар
                product = Product.objects.create(
                    name=product_data['name'],
                    price=product_data['price'],
                    manufacturer=manufacturer,
                    btu=product_data['btu'],
                    area_coverage=product_data['area_coverage'],
                    description=product_data['description'],
                    is_available=True
                )
                
                # Додаємо зображення
                for i, image_url in enumerate(product_data['images'], 1):
                    ProductImage.objects.create(
                        product=product,
                        image_url=f"/static/{image_url}",
                        alt_text=f"{product.name} - фото {i}"
                    )
                
                # Встановлюємо головне зображення
                if product_data['images']:
                    product.image_url = f"/static/{product_data['images'][0]}"
                    product.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Відновлено товар: {product.name} - {product.price} грн")
                )
                restored_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Помилка при відновленні товару {product_data['name']}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Успішно відновлено {restored_count} товарів!")
        )
        return restored_count
