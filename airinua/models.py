from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Назва виробника"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Виробник")
        verbose_name_plural = _("Виробники")
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
        ('20', _('До 20 м² (07 BTU)')),
        ('25', _('До 25 м² (09 BTU)')),
        ('35', _('До 35 м² (12 BTU)')),
        ('50', _('До 50 м² (18 BTU)')),
        ('60', _('До 60 м² (24 BTU)')),
        ('80', _('До 80 м² (28 BTU)')),
        ('100', _('До 100 м² (36 BTU)')),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Назва товару"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ціна, грн"))
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name=_("Виробник"))
    btu = models.CharField(max_length=3, choices=BTU_CHOICES, verbose_name=_("Потужність (BTU)"))
    area_coverage = models.CharField(max_length=3, choices=AREA_CHOICES, verbose_name=_("Площа покриття (м²)"))
    description = models.TextField(blank=True, verbose_name=_("Опис"))
    image = models.ImageField(upload_to='products/', verbose_name=_("Основне зображення"), blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name=_("В наявності"))

    def __str__(self):
        return f"{self.manufacturer} {self.name}"

    class Meta:
        verbose_name = _("Кондиціонер")
        verbose_name_plural = _("Кондиціонери")
        ordering = ['manufacturer', 'name']


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Назва послуги"))
    description = models.TextField(blank=True, verbose_name=_("Опис послуги"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ціна послуги, грн"))
    image = models.ImageField(upload_to='services/', verbose_name=_("Зображення послуги"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Послуга")
        verbose_name_plural = _("Послуги")
        ordering = ['name']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name=_("Товар"))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_("Зображення"))
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_("Альтернативний текст (для SEO)"))
    # Можна додати порядок сортування, якщо потрібно
    # sort_order = models.PositiveIntegerField(default=0, blank=False, null=False) 

    class Meta:
        verbose_name = _("Зображення товару")
        verbose_name_plural = _("Зображення товарів")
        # ordering = ['sort_order'] # Якщо додали сортування

    def __str__(self):
        return f"Зображення для {self.product.name}"


class FeedbackRequest(models.Model):
    name = models.CharField("Ім'я", max_length=255)
    phone = models.CharField("Телефон", max_length=20)
    contact_method = models.CharField("Спосіб зв'язку", max_length=10, choices=[('telegram', 'Telegram'), ('viber', 'Viber'), ('call', 'Подзвонити')])
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Товар", related_name="feedbacks")
    created_at = models.DateTimeField("Дата створення", auto_now_add=True)

    def __str__(self):
        if self.product:
            return f'Заявка від {self.name} ({self.phone}) на товар "{self.product.name}"'
        return f"Заявка від {self.name} ({self.phone})"

    class Meta:
        verbose_name = "Заявка на зворотній зв'язок"
        verbose_name_plural = "Заявки на зворотній зв'язок"
        ordering = ['-created_at']
