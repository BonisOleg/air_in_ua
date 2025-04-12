from django.urls import path
from . import views # Розкоментуємо імпорт views

app_name = 'airinua' # Додаємо ім'я простору для додатку

urlpatterns = [
    # Додай свої URL-шляхи тут
    path('', views.index, name='index'), # Шлях для головної сторінки
    path('catalog/', views.catalog_view, name='catalog'), # Шлях для каталогу

    # API Endpoints для AJAX
    path('api/products/filter/', views.filter_products, name='filter_products'),
    path('api/feedback/submit/', views.submit_feedback, name='submit_feedback'),
]
