from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Manufacturer, Product, Service, FeedbackRequest, ProductImage

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

# --- Інлайн для зображень товару ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Показувати одне порожнє поле для додавання за замовчуванням
    fields = ('image', 'alt_text') # Поля для редагування
    # Якщо додали сортування, можна використати readonly_fields = ('sort_order',)
    
# --- Кастомна форма для масового додавання з полями галереї ---
class ProductBulkForm(forms.ModelForm):
    # Додаємо до 10 полів для галереї
    gallery_image_1 = forms.ImageField(required=False, label=_("Фото галереї 1"))
    gallery_image_2 = forms.ImageField(required=False, label=_("Фото галереї 2"))
    gallery_image_3 = forms.ImageField(required=False, label=_("Фото галереї 3"))
    gallery_image_4 = forms.ImageField(required=False, label=_("Фото галереї 4"))
    gallery_image_5 = forms.ImageField(required=False, label=_("Фото галереї 5"))
    gallery_image_6 = forms.ImageField(required=False, label=_("Фото галереї 6"))
    gallery_image_7 = forms.ImageField(required=False, label=_("Фото галереї 7"))
    gallery_image_8 = forms.ImageField(required=False, label=_("Фото галереї 8"))
    gallery_image_9 = forms.ImageField(required=False, label=_("Фото галереї 9"))
    gallery_image_10 = forms.ImageField(required=False, label=_("Фото галереї 10"))

    class Meta:
        model = Product
        fields = ('name', 'manufacturer', 'price', 'btu', 'area_coverage', 'image', 'is_available',
                  # Не додаємо gallery_image сюди напряму, вони йдуть окремо
                 )

class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'price', 'btu', 'area_coverage', 'is_available')
    search_fields = ('name', 'description')
    list_filter = ('manufacturer', 'btu', 'area_coverage', 'is_available')
    list_editable = ('price', 'is_available')
    change_list_template = "admin/product_changelist.html"
    # Додаємо інлайн для зображень
    inlines = [ProductImageInline]
    fieldsets = (
        (_("Основна інформація"), {
            'fields': ('name', 'manufacturer', 'price')
        }),
        (_("Технічні характеристики"), {
            'fields': ('btu', 'area_coverage', 'description')
        }),
        (_("Головне зображення (для картки)"), { # Уточнено назву секції
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
        # Використовуємо нашу кастомну форму
        ProductFormSet = modelformset_factory(
            Product,
            # fields= ProductBulkForm.Meta.fields, # Визначаємо поля в формі
            form=ProductBulkForm, # Вказуємо кастомну форму
            extra=10
        )

        if request.method == 'POST':
            formset = ProductFormSet(request.POST, request.FILES, queryset=Product.objects.none())
            if formset.is_valid():
                instances = formset.save(commit=False) # Ще не зберігаємо в БД
                saved_count = 0
                gallery_images_added = 0
                
                for i, instance in enumerate(instances):
                    # Зберігаємо основний продукт
                    instance.save() 
                    saved_count += 1
                    
                    # Обробляємо додаткові зображення галереї
                    form = formset.forms[i] # Отримуємо конкретну форму з формсету
                    for j in range(1, 11): 
                        field_name = f'gallery_image_{j}'
                        image_file = form.cleaned_data.get(field_name)
                        if image_file:
                            ProductImage.objects.create(product=instance, image=image_file)
                            gallery_images_added += 1
                            
                if saved_count:
                     self.message_user(request, _("%(count)d товарів успішно додано. Додано %(gallery_count)d фото в галереї.") % {'count': saved_count, 'gallery_count': gallery_images_added})
                # formset.save() # Цей рядок більше не потрібен, бо ми зберегли вручну
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

# Реєстрація моделей через кастомний сайт
admin_site.register(Manufacturer, ManufacturerAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Service, ServiceAdmin)

# --- Додаткова реєстрація для стандартного admin.site --- #
from django.contrib import admin # Переконуємось, що стандартний admin імпортовано

admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
