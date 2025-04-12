document.addEventListener('DOMContentLoaded', () => {
    // --- Обробник для плаваючої кнопки та модального вікна ---
    const modal = document.getElementById('feedback-modal');
    const toggle = document.getElementById('feedback-toggle-btn');
    const closeButton = modal ? modal.querySelector('.modal-close') : null;

    if (toggle && modal) {
        toggle.addEventListener('click', function () {
            modal.style.display = 'flex';
        });
    }

    if (closeButton) {
        closeButton.addEventListener('click', function () {
            modal.style.display = 'none';
        });
    }

    if (modal) {
        modal.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
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
            e.preventDefault();

            const formData = new FormData(feedbackForm);
            const submitButton = feedbackForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;

            submitButton.disabled = true;
            submitButton.textContent = 'Надсилання...';

            fetch('/api/feedback/submit/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(errData.message || 'Помилка сервера');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message || 'Дякуємо! Ми звʼяжемось із вами.');
                        feedbackForm.reset();
                        if (modal) {
                            modal.style.display = 'none';
                        }
                    } else {
                        alert('Помилка при відправці: \n' + JSON.stringify(data.errors || 'Перевірте дані.'));
                        console.error('Validation errors:', data.errors);
                    }
                })
                .catch(error => {
                    console.error('Ajax error:', error);
                    alert('Помилка при відправці: ' + error.message);
                })
                .finally(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                });
        });
    }

    // --- Логіка AJAX-фільтрації товарів ---
    const filterForm = document.getElementById('product-filter-form');
    const productListContainer = document.getElementById('product-list-container');

    if (filterForm && productListContainer) {
        filterForm.addEventListener('input', handleFilterChange);
        filterForm.addEventListener('change', handleFilterChange);

        function handleFilterChange() {
            const formData = new FormData(filterForm);
            const params = new URLSearchParams();

            formData.forEach((value, key) => {
                if (value) {
                    params.append(key, value);
                }
            });

            const queryString = params.toString();
            const fetchUrl = `/api/products/filter/?${queryString}`;

            productListContainer.innerHTML = '<p>Оновлення...</p>';

            fetch(fetchUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    productListContainer.innerHTML = data.html;
                })
                .catch(error => {
                    console.error('Filter error:', error);
                    productListContainer.innerHTML = '<p>Помилка завантаження товарів.</p>';
                });
        }
    }

});
