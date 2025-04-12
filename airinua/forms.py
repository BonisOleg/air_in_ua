from django import forms
from .models import FeedbackRequest

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackRequest
        fields = ['name', 'phone', 'contact_method']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': "Ваше ім'я"}),
            'phone': forms.TextInput(attrs={'class': 'input', 'placeholder': "Номер телефону"}), # Використовуємо TextInput для гнучкості формату
            'contact_method': forms.Select(attrs={'class': 'input'}),
        }
        # Можна додати labels, якщо потрібно:
        # labels = {
        #     'name': "Ім'я",
        #     'phone': "Телефон",
        #     'contact_method': "Спосіб зв'язку",
        # }
