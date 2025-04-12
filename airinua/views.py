from django.shortcuts import render
from .models import Product # Імпортуємо модель Product
from .forms import FeedbackForm # Імпортуємо форму
from django.http import JsonResponse # Додаємо JsonResponse
from django.views.decorators.csrf import csrf_exempt # Додаємо csrf_exempt

# Create your views here.
def index(request):
    """Відображає головну сторінку сайту."""
    form = FeedbackForm() # Створюємо екземпляр форми
    context = {
        'form': form, # Передаємо форму в контекст
    }
    return render(request, 'index.html', context)

def catalog_view(request):
    """Відображає сторінку каталогу з доступними товарами."""
    products = Product.objects.filter(is_available=True)
    form = FeedbackForm() # Створюємо екземпляр форми
    context = {
        'products': products,
        'form': form, # Передаємо форму в контекст
    }
    return render(request, 'catalog.html', context)

# --- AJAX Endpoints --- 

def filter_products(request):
    """Заглушка для AJAX-фільтрації товарів."""
    # Тут буде логіка фільтрації на основі GET-параметрів
    # Поки що просто повертаємо статус ok
    return JsonResponse({'status': 'ok', 'message': 'filter ready'})

@csrf_exempt # УВАГА: Тимчасово для тестування. Потрібно налаштувати CSRF для AJAX.
def submit_feedback(request):
    """Обробляє AJAX-запит для форми зворотного зв'язку."""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save() # Зберігаємо заявку в базу даних
            return JsonResponse({'status': 'success', 'message': 'Заявку успішно відправлено!'})
        else:
            # Повертаємо помилки валідації
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400) # Повертаємо 400 Bad Request
    # Якщо метод не POST
    return JsonResponse({'status': 'invalid method', 'message': 'Будь ласка, використовуйте метод POST.'}, status=405) # Повертаємо 405 Method Not Allowed
