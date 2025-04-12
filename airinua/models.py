from django.db import models

# Create your models here.

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва виробника")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Виробник"
        verbose_name_plural = "Виробники"
        ordering = ['name']

class Product(models.Model):
    BTU_CHOICES = [
        ('07', '07 BTU'),
        ('09', '09 BTU'),
        ('12', '12 BTU'),
        ('18', '18 BTU'),
        ('24', '24 BTU'),
        ('28', '28 BTU'),
        ('36', '36 BTU'),
    ]
    # Зв'яжемо площу з BTU для логічності, як вказано в TZ для фільтрів
    AREA_CHOICES = [
        ('20', 'До 20 м² (07 BTU)'),
        ('25', 'До 25 м² (09 BTU)'),
        ('35', 'До 35 м² (12 BTU)'),
        ('50', 'До 50 м² (18 BTU)'),
        ('60', 'До 60 м² (24 BTU)'),
        ('80', 'До 80 м² (28 BTU)'),
        ('100', 'До 100 м² (36 BTU)'),
    ]

    name = models.CharField(max_length=255, verbose_name="Назва товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна, грн")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Виробник")
    btu = models.CharField(max_length=3, choices=BTU_CHOICES, verbose_name="Потужність (BTU)")
    area_coverage = models.CharField(max_length=3, choices=AREA_CHOICES, verbose_name="Площа покриття (м²)")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='products/', verbose_name="Основне зображення", blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name="В наявності")

    def __str__(self):
        return f"{self.manufacturer} {self.name}"

    class Meta:
        verbose_name = "Кондиціонер"
        verbose_name_plural = "Кондиціонери"
        ordering = ['manufacturer', 'name']


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва послуги")
    description = models.TextField(blank=True, verbose_name="Опис послуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна послуги, грн")
    image = models.ImageField(upload_to='services/', verbose_name="Зображення послуги", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ['name']


class FeedbackRequest(models.Model):
    CONTACT_CHOICES = [
        ('telegram', 'Telegram'),
        ('viber', 'Viber'),
        ('call', 'Дзвінок'),
    ]

    name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    phone = models.CharField(max_length=20, verbose_name="Телефон") # CharField краще для телефонів
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES, verbose_name="Спосіб зв'язку")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL, # Якщо товар видалять, заявка залишиться
        null=True,
        blank=True,
        verbose_name="Товар (якщо є)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        product_info = f" - {self.product}" if self.product else ""
        return f"Заявка від {self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')}){product_info}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at'] # Показувати новіші першими
