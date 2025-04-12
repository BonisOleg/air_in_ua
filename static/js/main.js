document.addEventListener('DOMContentLoaded', () => {
    // --- Обробник для плаваючої кнопки та основної модалки ---
    const modal = document.getElementById('feedback-modal');
    const toggle = document.getElementById('feedback-toggle-btn');
    const closeButton = modal ? modal.querySelector('.modal-close') : null;

    if (toggle && modal) {
        toggle.addEventListener('click', function () {
            modal.style.display = 'flex';
            // Знаходимо форму всередині цієї модалки і додаємо обробник
            const formInsideModal = modal.querySelector('#feedback-form-actual');
            if (formInsideModal) {
                addSubmitHandlerToForm(formInsideModal);
            }
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

    const feedbackForm = document.getElementById('feedback-form-actual');
    const formMessageDiv = feedbackForm ? feedbackForm.querySelector('.form-message') : null;

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(feedbackForm);
            const submitButton = feedbackForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            const actionUrl = feedbackForm.dataset.actionUrl;

            if (!actionUrl) {
                console.error('Form action URL not found!');
                if (formMessageDiv) formMessageDiv.innerHTML = `<p style="color: red;">Помилка конфігурації форми.</p>`;
                return;
            }

            // Очищуємо попереднє повідомлення
            if (formMessageDiv) formMessageDiv.innerHTML = '';
            submitButton.disabled = true;
            submitButton.textContent = 'Надсилання...';

            fetch(actionUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (formMessageDiv) {
                            formMessageDiv.innerHTML = `<p style="color: green;">${data.message || 'Дякуємо! Вашу заявку прийнято.'}</p>`;
                        }
                        feedbackForm.reset();
                        setTimeout(() => {
                            if (modal) {
                                modal.style.display = 'none';
                            }
                            if (formMessageDiv) formMessageDiv.innerHTML = '';
                        }, 4000);
                    } else {
                        let errorMessage = 'Помилка при відправці.<br>';
                        if (data.errors) {
                            for (const field in data.errors) {
                                errorMessage += `- ${field}: ${data.errors[field].join(', ')}<br>`;
                            }
                        } else {
                            errorMessage += data.message || 'Будь ласка, перевірте введені дані.';
                        }
                        if (formMessageDiv) {
                            formMessageDiv.innerHTML = `<p style="color: red;">${errorMessage}</p>`;
                        }
                    }
                })
                .catch(error => {
                    console.error('Ajax error:', error);
                    if (formMessageDiv) {
                        formMessageDiv.innerHTML = `<p style="color: red;">Не вдалося відправити форму. Спробуйте пізніше.</p>`;
                    }
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
                    initializeProductCardClicks();
                })
                .catch(error => {
                    console.error('Filter error:', error);
                    productListContainer.innerHTML = '<p>Помилка завантаження товарів.</p>';
                });
        }
    }

    // --- Логіка для модального вікна деталей товару ---
    const productModal = document.getElementById('product-modal');
    const productModalContent = document.getElementById('product-modal-content');
    const productModalCloseButton = productModal ? productModal.querySelector('.modal-close') : null;

    function initializeProductCardClicks() {
        const productCards = document.querySelectorAll('#product-list-container .product-card');
        productCards.forEach(card => {
            if (!card.dataset.clickListenerAdded) {
                card.addEventListener('click', function () {
                    const productId = this.dataset.id;
                    productModalContent.innerHTML = '<p>Завантаження...</p><button class="modal-close">Закрити</button>';
                    productModal.style.display = 'flex';

                    fetch(`/api/product/${productId}/`)
                        .then(response => response.text())
                        .then(html => {
                            productModalContent.innerHTML = html;
                            // Знаходимо форму ПІСЛЯ додавання HTML
                            const modalForm = productModalContent.querySelector('#feedback-form-actual');
                            if (modalForm) {
                                // Додаємо обробник submit до форми в модалці товару
                                addSubmitHandlerToForm(modalForm);
                            }
                            // Додаємо кнопку закриття
                            const closeBtn = productModalContent.querySelector('.modal-close');
                            if (closeBtn) {
                                closeBtn.addEventListener('click', closeProductModal);
                            }
                        })
                        .catch(error => {
                            console.error('Product detail error:', error);
                            productModalContent.innerHTML = `<p>${error.message}</p>`;
                            if (productModalCloseButton) {
                                productModalContent.appendChild(productModalCloseButton.cloneNode(true));
                                const errorCloseButton = productModalContent.querySelector('.modal-close');
                                if (errorCloseButton) {
                                    errorCloseButton.addEventListener('click', closeProductModal);
                                }
                            } else {
                                productModalContent.innerHTML += '<button class="modal-close">Закрити</button>';
                                const newErrorCloseButton = productModalContent.querySelector('.modal-close');
                                if (newErrorCloseButton) {
                                    newErrorCloseButton.addEventListener('click', closeProductModal);
                                }
                            }
                        });
                });
                card.dataset.clickListenerAdded = 'true';
            }
        });
    }

    // --- Універсальна функція додавання обробника submit ---
    function addSubmitHandlerToForm(formElement) {
        // Перевіряємо, чи обробник вже не додано, щоб уникнути дублів
        if (formElement.dataset.submitHandlerAttached === 'true') return;

        const formMessageDiv = formElement.querySelector('.form-message');

        formElement.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(formElement);
            const submitButton = formElement.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            const actionUrl = formElement.dataset.actionUrl;

            if (!actionUrl) {
                console.error('Form action URL not found!');
                if (formMessageDiv) formMessageDiv.innerHTML = `<p style="color: red;">Помилка конфігурації форми.</p>`;
                return;
            }

            if (formMessageDiv) formMessageDiv.innerHTML = '';
            submitButton.disabled = true;
            submitButton.textContent = 'Надсилання...';

            fetch(actionUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (formMessageDiv) {
                            formMessageDiv.innerHTML = `<p style="color: green;">${data.message || 'Дякуємо! Вашу заявку прийнято.'}</p>`;
                        }
                        formElement.reset();
                        setTimeout(() => {
                            // Закриваємо тільки модалку товару, а не основну
                            if (formElement.closest('#product-modal')) {
                                closeProductModal();
                            } else if (formElement.closest('#feedback-modal')) {
                                const mainFeedbackModal = document.getElementById('feedback-modal');
                                if (mainFeedbackModal) mainFeedbackModal.style.display = 'none';
                            }
                            if (formMessageDiv) formMessageDiv.innerHTML = '';
                        }, 4000);
                    } else {
                        let errorMessage = 'Помилка при відправці.<br>';
                        if (data.errors) {
                            for (const field in data.errors) {
                                errorMessage += `- ${field}: ${data.errors[field].join(', ')}<br>`;
                            }
                        } else {
                            errorMessage += data.message || 'Будь ласка, перевірте введені дані.';
                        }
                        if (formMessageDiv) {
                            formMessageDiv.innerHTML = `<p style="color: red;">${errorMessage}</p>`;
                        }
                    }
                })
                .catch(error => {
                    console.error('Ajax error:', error);
                    if (formMessageDiv) {
                        formMessageDiv.innerHTML = `<p style="color: red;">Не вдалося відправити форму. Спробуйте пізніше.</p>`;
                    }
                })
                .finally(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                });
        });

        formElement.dataset.submitHandlerAttached = 'true'; // Позначаємо, що обробник додано
    }

    // --- Функція закриття модалки товару ---
    function closeProductModal() {
        if (productModal) {
            productModal.style.display = 'none';
            productModalContent.innerHTML = '<button class="modal-close">Закрити</button>';
        }
    }

    if (productModal) {
        productModal.addEventListener('click', function (event) {
            if (event.target === productModal) {
                closeProductModal();
            }
        });
    }

    if (productModalCloseButton) {
        productModalCloseButton.addEventListener('click', closeProductModal);
    }

    initializeProductCardClicks();

});
