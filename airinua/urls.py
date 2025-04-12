from django.urls import path
from . import views # Розкоментуємо імпорт views

app_name = 'airinua' # Додаємо ім'я простору для додатку

urlpatterns = [
    # Додай свої URL-шляхи тут
    path('', views.index, name='index'), # Шлях для головної сторінки
    path('catalog/', views.catalog_view, name='catalog'), # Шлях для каталогу
    path('services/', views.services_view, name='services'), # Шлях для послуг
    path('about/', views.about_view, name='about'), # Шлях для сторінки "Про нас"

    # API Endpoints для AJAX
    path('api/products/filter/', views.filter_products, name='filter_products'),
    path('api/feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('api/product/<int:product_id>/', views.product_detail_modal, name='product_modal'), # Новий ендпоінт
]
