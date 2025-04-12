from django.shortcuts import render, get_object_or_404
from .models import Product, Manufacturer, Service # Додаємо Service
# FeedbackForm тут більше не потрібна напряму
from django.http import JsonResponse # Додаємо JsonResponse
# csrf_exempt більше не потрібен
from django.template.loader import render_to_string # Для рендерингу HTML-фрагменту
from .forms import FeedbackForm # Імпортуємо для submit_feedback

# Create your views here.
def index(request):
    """Відображає головну сторінку сайту."""
    # Форма тепер глобально в контексті завдяки процесору
    context = {}
    return render(request, 'index.html', context)

def catalog_view(request):
    """Відображає сторінку каталогу з доступними товарами."""
    products = Product.objects.filter(is_available=True)
    manufacturers = Manufacturer.objects.all() # Отримуємо виробників для фільтра
    # Форма тепер глобально в контексті
    context = {
        'products': products,
        'manufacturers': manufacturers, # Передаємо виробників
    }
    return render(request, 'catalog.html', context)

def services_view(request):
    """Відображає сторінку з переліком послуг."""
    services = Service.objects.all() # Отримуємо всі послуги
    # Форма тепер глобально в контексті
    context = {
        'services': services,
    }
    return render(request, 'services.html', context)

def about_view(request):
    """Відображає сторінку 'Про нас'."""
    # Форма тепер глобально в контексті
    context = {}
    return render(request, 'about.html', context)

# --- AJAX Endpoints --- 

def filter_products(request):
    """Фільтрує товари за GET-параметрами та повертає HTML-фрагмент."""
    products = Product.objects.filter(is_available=True)

    # Отримуємо значення фільтрів з GET-запиту
    manufacturer_id = request.GET.get('manufacturer')
    btu = request.GET.get('btu')
    area = request.GET.get('area') # Зверни увагу на модельне поле - area_coverage
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    # Застосовуємо фільтри, якщо вони є
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
    if btu:
        products = products.filter(btu=btu)
    if area:
        # Важливо: Треба адаптувати фільтрацію площі до значень у AREA_CHOICES.
        # Наприклад, якщо area='20', треба фільтрувати продукти, де area_coverage='20'.
        # Якщо модельне поле area_coverage зберігає лише число, можливо знадобиться інша логіка.
        # Припускаємо, що area_coverage зберігає значення '20', '25' і т.д.
        products = products.filter(area_coverage=area)
    if price_min:
        try:
            products = products.filter(price__gte=price_min)
        except ValueError: # Обробка, якщо введено не число
            pass
    if price_max:
        try:
            products = products.filter(price__lte=price_max)
        except ValueError:
            pass
            
    # Рендеримо відфільтрований список товарів у HTML-рядок
    html = render_to_string(
        'includes/product_list.html', 
        {'products': products}
    )
    # Повертаємо HTML у JSON-відповіді
    return JsonResponse({'html': html})

def submit_feedback(request):
    """Обробляє AJAX-запит для форми зворотного зв'язку."""
    if request.method == 'POST':
        # Використовуємо форму напряму, не передаючи її в контекст
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save() # Зберігаємо заявку в базу даних
            return JsonResponse({'status': 'success', 'message': 'Заявку успішно відправлено!'})
        else:
            # Повертаємо помилки валідації
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400) # Повертаємо 400 Bad Request
    # Якщо метод не POST
    return JsonResponse({'status': 'invalid method', 'message': 'Будь ласка, використовуйте метод POST.'}, status=405) # Повертаємо 405 Method Not Allowed

def product_detail_modal(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'includes/product_modal_detail.html', {'product': product})
