from django.shortcuts import render, get_object_or_404
from .models import Product, Manufacturer, Service, FeedbackRequest # Додано FeedbackRequest
# FeedbackForm тут більше не потрібна напряму
from django.http import JsonResponse, HttpResponseNotFound # Додаємо JsonResponse та HttpResponseNotFound
# csrf_exempt більше не потрібен
from django.template.loader import render_to_string # Для рендерингу HTML-фрагменту
from .forms import FeedbackForm # Імпортуємо для submit_feedback
from django.core.mail import EmailMultiAlternatives # Замінюємо send_mail на EmailMultiAlternatives
from django.conf import settings # Для отримання ADMIN_EMAIL
import logging
# Додаємо імпорти для пагінації
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 

# Отримуємо logger
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    """Відображає головну сторінку сайту."""
    # Форма тепер глобально в контексті завдяки процесору
    context = {}
    return render(request, 'index.html', context)

def catalog_view(request):
    """Відображає сторінку каталогу з доступними товарами та пагінацією."""
    # products = Product.objects.filter(is_available=True)
    product_list = Product.objects.filter(is_available=True) # Спочатку просто фільтруємо
    manufacturers = Manufacturer.objects.all() # Отримуємо виробників для фільтра
    feedback_form = FeedbackForm() # Створюємо екземпляр форми

    # Отримуємо параметр сортування
    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'price_asc':
        product_list = product_list.order_by('price')
    elif sort_by == 'price_desc':
        product_list = product_list.order_by('-price')
    else:
        # За замовчуванням сортуємо за назвою
        product_list = product_list.order_by('name') 

    # Налаштування пагінації (після сортування)
    paginator = Paginator(product_list, 15) # 15 товарів на сторінку
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # Якщо номер сторінки не ціле число, показуємо першу сторінку
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # Якщо номер сторінки поза діапазоном, показуємо останню сторінку
        page_obj = paginator.get_page(paginator.num_pages)
    
    context = {
        # 'products': products, # Замінюємо повний список на об'єкт сторінки
        'page_obj': page_obj,
        'manufacturers': manufacturers, # Передаємо виробників
        'form': feedback_form, # Додаємо форму до контексту
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
    sort_by = request.GET.get('sort_by', '') # Отримуємо сортування

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
            
    # Застосовуємо сортування
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        # За замовчуванням сортуємо за назвою для AJAX, або залиш як є, якщо фільтри вже щось відсортували
        products = products.order_by('name')

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
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Отримуємо ID товару з запиту, якщо він є
            product_id = request.POST.get('product_id')
            product = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    # Можна повернути помилку або просто проігнорувати, 
                    # якщо ID неправильний
                    pass 
            
            # Отримуємо ID послуги з запиту, якщо він є
            service_id = request.POST.get('service_id')
            service = None
            if service_id:
                try:
                    service = Service.objects.get(id=service_id)
                except Service.DoesNotExist:
                    pass

            # Отримуємо джерело запиту
            request_source = request.POST.get('request_source')
            is_master_call = request_source == 'master_call'

            # Зберігаємо форму, але поки не в БД
            feedback = form.save(commit=False)
            # Встановлюємо зв'язок з товаром (якщо є)
            feedback.product = product
            # Можливо, в майбутньому додати поле service до моделі FeedbackRequest?
            # Поки що не зберігаємо зв'язок з послугою в базі, лише в листі.
            feedback.save()
            
            # --- Відправка Email з HTML та Text версіями --- 
            subject = 'Нова заявка з сайту Air In UA'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [settings.ADMIN_EMAIL]
            
            # --- Прибираємо генерацію URL зображення --- 
            # image_url = None
            # if product and product.image:
            #     scheme = request.scheme
            #     host = request.get_host()
            #     image_url = f"{scheme}://{host}{product.image.url}"
            # --- Кінець прибирання URL ---

            # Контекст для рендерингу шаблонів
            context = {
                'name': form.cleaned_data['name'],
                'phone': form.cleaned_data['phone'],
                'contact_method_display': feedback.get_contact_method_display(),
                'product': product,
                'service': service, # Додаємо послугу до контексту
                'is_master_call': is_master_call, # Додаємо прапорець виклику майстра
                # 'product_image_url': image_url, # Більше не передаємо URL
            }
            
            # Рендеримо текстову та HTML версії
            text_content = render_to_string('email/feedback_notification.txt', context)
            html_content = render_to_string('email/feedback_notification.html', context)
            
            try:
                # Створюємо лист з обома версіями
                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                # Логування помилки через стандартний logging
                logger.error(f"Помилка відправки email: {e}")
            # --- Кінець відправки Email ---

            return JsonResponse({'status': 'success', 'message': 'Заявку успішно відправлено!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'invalid method', 'message': 'Будь ласка, використовуйте метод POST.'}, status=405)

def product_detail_modal(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'includes/product_modal_detail.html', {'product': product})

def error_404_view(request, exception=None):
    """
    Обробник для помилки 404 (Сторінку не знайдено)
    """
    return render(request, 'errors/404.html', status=404)


def error_500_view(request, exception=None):
    """
    Обробник для помилки 500 (Внутрішня помилка сервера)
    """
    return render(request, 'errors/500.html', status=500)


def error_403_view(request, exception=None):
    """
    Обробник для помилки 403 (Доступ заборонено)
    """
    return render(request, 'errors/403.html', status=403)
