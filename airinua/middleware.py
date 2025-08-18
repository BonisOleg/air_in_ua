"""
Middleware для обслуговування медіафайлів на production (Render).
"""
import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils._os import safe_join
from django.views.static import serve


class MediaFileMiddleware:
    """
    Middleware для обслуговування медіафайлів через Django на production.
    Використовується тільки коли DEBUG=False (на Render).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Обробляємо тільки запити до медіафайлів
        if request.path.startswith(settings.MEDIA_URL):
            # Видаляємо MEDIA_URL з початку шляху
            relative_path = request.path[len(settings.MEDIA_URL):]
            
            try:
                # Безпечно об'єднуємо шлях з MEDIA_ROOT
                full_path = safe_join(settings.MEDIA_ROOT, relative_path)
                
                # Перевіряємо чи файл існує
                if os.path.isfile(full_path):
                    return serve(request, relative_path, document_root=settings.MEDIA_ROOT)
                else:
                    # Якщо файл не знайдено - повертаємо placeholder або 404
                    if 'products/' in relative_path:
                        # Для товарів повертаємо placeholder
                        placeholder_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'img', 'placeholder.png')
                        if os.path.isfile(placeholder_path):
                            return serve(request, 'img/placeholder.png', document_root=settings.STATIC_ROOT or settings.STATICFILES_DIRS[0])
                    
                    raise Http404("Media file not found")
                    
            except (ValueError, Http404):
                # Якщо шлях небезпечний або файл не знайдено
                raise Http404("Media file not found")
        
        # Передаємо запит далі якщо це не медіафайл
        response = self.get_response(request)
        return response
