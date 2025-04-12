from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Manufacturer, Product, Service, FeedbackRequest

# --- Кастомний Admin Site ---
class UAAdminSite(admin.AdminSite):
    site_header = _("Панель керування Air In UA")
    site_title = _("Air In UA Адмін") # Заголовок вкладки
    index_title = _("Керування сайтом")

    # Не обов'язково, але для консистентності
    def each_context(self, request):
        context = super().each_context(request)
        # Переконаємось, що всі потрібні змінні мають той самий заголовок
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['index_title'] = self.index_title
        return context

admin_site = UAAdminSite(name='uaadmin')

# --- Моделі Адмінки ---

class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'price', 'btu', 'area_coverage', 'is_available')
    search_fields = ('name', 'description')
    list_filter = ('manufacturer', 'btu', 'area_coverage', 'is_available')
    list_editable = ('price', 'is_available')
    change_list_template = "admin/product_changelist.html"
    fieldsets = (
        (_("Основна інформація"), {
            'fields': ('name', 'manufacturer', 'price')
        }),
        (_("Технічні характеристики"), {
            'fields': ('btu', 'area_coverage', 'description')
        }),
        (_("Зображення та доступність"), {
            'fields': ('image', 'is_available')
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk_add/', self.admin_site.admin_view(self.bulk_add_products_view), name='airinua_product_bulk_add'),
        ]
        return custom_urls + urls

    def bulk_add_products_view(self, request):
        ProductFormSet = modelformset_factory(
            Product,
            fields=('name', 'manufacturer', 'price', 'btu', 'area_coverage', 'image', 'is_available'),
            extra=10
        )

        if request.method == 'POST':
            formset = ProductFormSet(request.POST, request.FILES, queryset=Product.objects.none())
            if formset.is_valid():
                formset.save()
                self.message_user(request, _("Товари успішно додано."))
                return redirect('..')
            else:
                self.message_user(request, _("Будь ласка, виправте помилки нижче."), level='error')
        else:
            formset = ProductFormSet(queryset=Product.objects.none())

        context = {
            **self.admin_site.each_context(request),
            'title': _('Масове додавання товарів'),
            'formset': formset,
        }
        return render(request, 'admin/bulk_add_products.html', context)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name', 'description')
    list_editable = ('price',)
    fieldsets = (
        (None, {'fields': ('name', 'price')}),
        (_("Деталі"), {'fields': ('description', 'image'), 'classes': ('collapse',)}),
    )

@admin.register(FeedbackRequest, site=admin_site) # Реєструємо через декоратор для кастомної адмінки
@admin.register(FeedbackRequest, site=admin.site) # Реєструємо через декоратор для стандартної адмінки
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'contact_method', 'product', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('contact_method', 'created_at', 'product')
    # Зробимо поля тільки для читання, щоб не можна було змінити заявку
    readonly_fields = ('created_at', 'product', 'name', 'phone', 'contact_method') 
    fieldsets = (
        (_("Інформація про клієнта"), {'fields': ('name', 'phone', 'contact_method')}),
        (_("Деталі заявки"), {'fields': ('product', 'created_at')}),
    )

    def has_add_permission(self, request):
        return False # Забороняємо створювати заявки через адмінку

    def has_delete_permission(self, request, obj=None):
        return False # Забороняємо видаляти заявки

# Реєстрація моделей через кастомний сайт
admin_site.register(Manufacturer, ManufacturerAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Service, ServiceAdmin)

# --- Додаткова реєстрація для стандартного admin.site --- #
from django.contrib import admin # Переконуємось, що стандартний admin імпортовано

admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)

# Закоментовані @admin.register залишаються закоментованими
# @admin.register(Manufacturer)
# @admin.register(Product)
# @admin.register(Service)
# @admin.register(FeedbackRequest)
