from .forms import FeedbackForm

def feedback_form_context(request):
    """Додає екземпляр FeedbackForm до контексту всіх шаблонів."""
    return {'feedback_form': FeedbackForm()} 