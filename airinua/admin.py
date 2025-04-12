from django.contrib import admin
from .models import Manufacturer, Product, Service, FeedbackRequest

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name'] # Додамо пошук і для виробників

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'price', 'btu', 'area_coverage', 'is_available')
    search_fields = ('name', 'description') # Додамо і опис до пошуку
    list_filter = ('manufacturer', 'btu', 'area_coverage', 'is_available') # Додамо фільтр за наявністю
    list_editable = ('price', 'is_available') # Дозволимо редагувати ціну та наявність прямо у списку

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name', 'description')
    list_editable = ('price',)

@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'contact_method', 'product', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('contact_method', 'created_at', 'product') # Додамо фільтри для зручності
    readonly_fields = ('created_at', 'product', 'name', 'phone', 'contact_method') # Зробимо поля заявки тільки для читання

    # Забороняємо додавання заявок через адмінку
    def has_add_permission(self, request):
        return False

    # Забороняємо видалення заявок через адмінку (краще архівувати, якщо треба)
    def has_delete_permission(self, request, obj=None):
        return False # Поки що заборонимо

# Register your models here.
# Можна також реєструвати так:
# admin.site.register(Manufacturer, ManufacturerAdmin)
# admin.site.register(Product, ProductAdmin)
# ... etc.
