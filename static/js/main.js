document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('toggle-feedback-form');
    const formContainer = document.getElementById('feedback-form-container');

    if (toggleBtn && formContainer) {
        toggleBtn.addEventListener('click', () => {
            // Перевіряємо поточний стан display і змінюємо на протилежний
            const isHidden = formContainer.style.display === 'none' || formContainer.style.display === '';
            formContainer.style.display = isHidden ? 'block' : 'none';
        });
    }

    // Функція для отримання CSRF-токену з cookies
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Запобігаємо стандартній відправці

            const formData = new FormData(feedbackForm);
            const submitButton = feedbackForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;

            // Показуємо, що йде відправка
            submitButton.disabled = true;
            submitButton.textContent = 'Надсилання...';

            fetch('/api/feedback/submit/', { // Використовуємо наш API endpoint
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(), // Додаємо CSRF-токен
                    // 'Content-Type': 'application/json' // Не потрібно для FormData
                },
                body: formData // Відправляємо дані форми
            })
                .then(response => {
                    if (!response.ok) {
                        // Якщо статус відповіді не 2xx, обробляємо як помилку
                        return response.json().then(errData => {
                            throw new Error(errData.message || 'Помилка сервера');
                        });
                    }
                    return response.json(); // Парсимо JSON-відповідь
                })
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message || 'Дякуємо! Ми звʼяжемось із вами.');
                        feedbackForm.reset(); // Очищуємо форму
                        // Можна також сховати форму після успішної відправки
                        if (formContainer) {
                            formContainer.style.display = 'none';
                        }
                    } else {
                        // Показуємо помилку, якщо статус 'error'
                        alert('Помилка при відправці: \n' + JSON.stringify(data.errors || 'Перевірте дані.'));
                        console.error('Validation errors:', data.errors);
                    }
                })
                .catch(error => {
                    console.error('Ajax error:', error);
                    alert('Помилка при відправці: ' + error.message);
                })
                .finally(() => {
                    // Повертаємо кнопку до початкового стану незалежно від результату
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                });
        });
    }

    // Тут буде інша JS логіка (напр., для AJAX)
});
