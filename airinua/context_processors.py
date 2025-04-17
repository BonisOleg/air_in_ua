from .forms import FeedbackForm

def feedback_form_context(request):
    """Додає екземпляр FeedbackForm до контексту всіх шаблонів під ключем 'form'."""
    return {'form': FeedbackForm()} 