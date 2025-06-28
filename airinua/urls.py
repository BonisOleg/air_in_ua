from django.urls import path
from . import views # Розкоментуємо імпорт views

app_name = 'airinua' # Додаємо ім'я простору для додатку

urlpatterns = [
    # Головні сторінки
    path('', views.index, name='index'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('services/', views.services_view, name='services'),
    path('about/', views.about_view, name='about'),
    
    # SEO-оптимізовані сторінки послуг
    path('montazh-kondytsioneriv-kyiv/', views.montazh_view, name='montazh-kondytsioneriv-kyiv'),
    path('servis-kondytsioneriv-kyiv/', views.servis_view, name='servis-kondytsioneriv-kyiv'),
    path('chystka-kondytsioneriv-kyiv/', views.chystka_view, name='chystka-kondytsioneriv-kyiv'),
    path('remont-kondytsioneriv-kyiv/', views.remont_view, name='remont-kondytsioneriv-kyiv'),
    path('zapravka-kondytsioneriv-kyiv/', views.zapravka_view, name='zapravka-kondytsioneriv-kyiv'),
    
    # Додаткові сторінки
    path('contacts/', views.contacts_view, name='contacts'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('faq/', views.faq_view, name='faq'),

    # API Endpoints для AJAX
    path('api/products/filter/', views.filter_products, name='filter_products'),
    path('api/feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('api/product/<int:product_id>/', views.product_detail_modal, name='product_modal'),
]
