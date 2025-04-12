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


class FeedbackRequest(models.Model):
    CONTACT_CHOICES = [
        ('telegram', 'Telegram'),
        ('viber', 'Viber'),
        ('call', _('Дзвінок')),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Ім'я клієнта"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES, verbose_name=_("Спосіб зв'язку"))
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL, # Якщо товар видалять, заявка залишиться
        null=True,
        blank=True,
        verbose_name=_("Товар (якщо є)")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата створення"))

    def __str__(self):
        product_info = f" - {self.product}" if self.product else ""
        return f"Заявка від {self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')}){product_info}"

    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")
        ordering = ['-created_at'] # Показувати новіші першими
