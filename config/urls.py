"""
URL Configuration for the project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.views.static import serve # Переконайся, що цей імпорт закоментовано або видалено
from airinua.admin import admin_site # Якщо використовуєш кастомну адмінку

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uaadmin/', admin_site.urls), # Якщо використовуєш кастомну адмінку
    path('', include('airinua.urls')), # Підключення URL додатку airinua
]

# Статичні файли (CSS, JavaScript, Images) в режимі Debug
if settings.DEBUG:
    # В DEBUG режимі Django сам обслуговує статику і медіа
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# В продакшені (DEBUG=False) статику обслуговує WhiteNoise.
# Медіа МАЄ обслуговувати веб-сервер (LiteSpeed), але поки він не налаштований,
# використовуємо тимчасове рішення нижче.

# --- ТИМЧАСОВЕ РІШЕННЯ ---
# Обслуговування медіафайлів через Django при DEBUG=False.
# Використовувати тільки до моменту налаштування LiteSpeed!
# Після налаштування LiteSpeed цей блок потрібно видалити або закоментувати.
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- КІНЕЦЬ ТИМЧАСОВОГО РІШЕННЯ ---

# Обробники помилок
handler404 = 'airinua.views.error_404_view'
handler500 = 'airinua.views.error_500_view'
handler403 = 'airinua.views.error_403_view'
