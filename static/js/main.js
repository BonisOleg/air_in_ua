document.addEventListener('DOMContentLoaded', () => {
    console.log('Global main.js loaded');

    // --- Обробка бургер-меню на мобільних ---
    const burgerMenu = document.querySelector('.burger-menu');
    const nav = document.querySelector('.nav');

    if (burgerMenu) {
        burgerMenu.addEventListener('click', () => {
            burgerMenu.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });

        // Закриваємо меню при кліку на посилання
        const navLinks = document.querySelectorAll('.nav a, .nav button');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                burgerMenu.classList.remove('active');
                nav.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
        });
    }

    // --- Обробка кліків на hero-блоках на головній --- 
    const heroOptions = document.querySelectorAll('.hero-option[data-url]');
    if (heroOptions.length > 0) {
        console.log('Found hero options:', heroOptions.length);
        heroOptions.forEach(option => {
            option.addEventListener('click', function () {
                const url = this.dataset.url;
                if (url) {
                    console.log('Hero option clicked. Redirecting to:', url);
                    window.location.href = url;
                } else {
                    console.warn('Hero option clicked, but data-url attribute is missing or empty.');
                }
            });
        });
    } else {
        // Це нормально, якщо ми не на головній сторінці
        // console.log('No hero options with data-url found on this page.');
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
                    // Тут дуже важливо перестворити обробники подій для модалок товарів
                    // та всі скрипти, які мають працювати з новими елементами
                    initProductCardEvents();
                    observeElements(); // Перезапускаємо анімацію появи
                })
                .catch(error => {
                    console.error('Filter error:', error);
                    productListContainer.innerHTML = '<p>Помилка завантаження товарів.</p>';
                });
        }
    }

    // --- Функція для ініціалізації всіх подій на картках товарів ---
    function initProductCardEvents() {
        // Ініціалізуємо модальні вікна товарів
        document.querySelectorAll('.article-modal-trigger').forEach(trigger => {
            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                console.log('[Main] Article modal trigger clicked');
                const card = this.closest('.article-card');
                if (!card) return;

                const articleModal = document.getElementById('articleModal');
                if (!articleModal) return;

                const articleModalContent = articleModal.querySelector('.modal-full-content');
                const articleModalTitle = articleModal.querySelector('.modal-title');
                const serviceModalContent = articleModal.querySelector('.service-modal-content');

                // Отримуємо дані, перевіряючи наявність кожного елемента
                const titleElement = card.querySelector('.article-card-title');
                const title = titleElement ? titleElement.textContent : 'Послуга';
                const contentId = card.dataset.modalContentId;
                const imageSrc = card.dataset.imageSrc;
                const fullContentElement = document.getElementById(contentId);

                // Встановлюємо зображення як фон модального вікна
                if (serviceModalContent && imageSrc) {
                    serviceModalContent.style.backgroundImage = `url('${imageSrc}')`;
                    serviceModalContent.classList.add('is-service-modal');
                    serviceModalContent.style.backgroundSize = '100% auto';

                    // Анімуємо масштабування фонового зображення для кращого візуального ефекту
                    setTimeout(() => {
                        serviceModalContent.style.backgroundSize = '110% auto';
                        serviceModalContent.style.transition = 'background-size 0.8s ease-in-out';
                    }, 100);
                }

                // Встановлюємо вміст тільки якщо існують обидва елементи
                if (articleModalContent && fullContentElement) {
                    articleModalContent.innerHTML = fullContentElement.innerHTML;
                    // ---- Додаємо логіку для галереї ПІСЛЯ вставки контенту ----
                    const galleryContainer = articleModalContent.querySelector('.product-gallery-container');
                    if (galleryContainer) {
                        const mainImage = galleryContainer.querySelector('.active-gallery-image');
                        const thumbnailsContainer = galleryContainer.querySelector('.gallery-thumbnails'); // Знаходимо батьківський контейнер мініатюр

                        if (mainImage && thumbnailsContainer) { // Перевіряємо наявність обох
                            // Використовуємо делегування подій
                            thumbnailsContainer.addEventListener('click', function (event) {
                                const clickedThumb = event.target.closest('.gallery-thumb'); // Перевіряємо, чи клікнули на мініатюру

                                if (!clickedThumb) return; // Якщо клік не по мініатюрі, нічого не робимо

                                const fullSrc = clickedThumb.dataset.fullSrc;
                                const altText = clickedThumb.alt.replace('Мініатюра: ', '');

                                if (fullSrc) {
                                    mainImage.src = fullSrc;
                                    mainImage.alt = altText;

                                    // Оновлюємо активну мініатюру
                                    thumbnailsContainer.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active-thumb'));
                                    clickedThumb.classList.add('active-thumb');
                                }
                            });
                        }
                    }
                    // ---- Кінець логіки галереї ----
                } else if (articleModalContent) {
                    articleModalContent.innerHTML = '<p>Помилка завантаження деталей.</p>';
                }

                articleModal.classList.add('is-open');
                document.body.classList.add('modal-open');
            });
        });
    }

    // --- Функція для анімації появи елементів ---
    function observeElements() {
        const elements = document.querySelectorAll('.reveal-on-scroll');
        if (!elements.length) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        elements.forEach(element => observer.observe(element));
    }

    // --- Закриття модальних вікон ---
    document.querySelectorAll('.article-modal-close, .article-modal-overlay').forEach(closer => {
        closer.addEventListener('click', function () {
            const articleModal = document.getElementById('articleModal');
            if (articleModal) {
                articleModal.classList.remove('is-open');
                document.body.classList.remove('modal-open');
                // Очищаємо фонове зображення при закритті
                const serviceModalContent = articleModal.querySelector('.service-modal-content');
                if (serviceModalContent) {
                    serviceModalContent.style.backgroundImage = '';
                    serviceModalContent.style.backgroundSize = '';
                    serviceModalContent.style.transition = '';
                    serviceModalContent.classList.remove('is-service-modal');
                }
            }
        });
    });

    // Запускаємо всі необхідні ініціалізації під час завантаження сторінки
    initProductCardEvents();
    observeElements();

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
                            // Закриваємо тільки модалку товару
                            if (formElement.closest('#product-modal')) {
                                closeProductModal();
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
    observeElements();

    // --- Обробник для кнопок, що відкривають ГЛОБАЛЬНУ форму без ID --- 
    document.querySelectorAll('.open-global-feedback-btn').forEach(button => {
        console.log('Found button to open global feedback:', button);
        button.addEventListener('click', function () {
            console.log('Generic open feedback button clicked.');
            if (typeof window.openGlobalFeedbackModal === 'function') {
                // Додаємо джерело запиту 'master_call' для цієї конкретної кнопки
                window.openGlobalFeedbackModal({ source: 'master_call' });
            } else {
                console.error('Global function openGlobalFeedbackModal is not defined!');
            }
        });
    });

    // --- Робота з ГЛОБАЛЬНИМ модальним вікном ФОРМИ --- 
    const feedbackModal = document.getElementById('feedbackModal');
    const feedbackModalClose = feedbackModal ? feedbackModal.querySelector('.feedback-modal-close') : null;
    const feedbackModalOverlay = feedbackModal ? feedbackModal.querySelector('.feedback-modal-overlay') : null;
    const feedbackForm = feedbackModal ? feedbackModal.querySelector('#feedback-form-actual') : null;
    const feedbackFormMessageContainer = feedbackModal ? feedbackModal.querySelector('.form-message') : null;
    const callMeButton = document.querySelector('.call-me-button'); // Кнопка "Подзвоніть мені"

    console.log('Global Feedback Modal elements:', { feedbackModal, feedbackModalClose, feedbackModalOverlay, feedbackForm, feedbackFormMessageContainer, callMeButton });

    if (!feedbackModal) {
        console.warn('Global feedback modal (#feedbackModal) not found on this page.');
    } else {
        // Глобальна функція для відкриття модалки форми
        window.openGlobalFeedbackModal = function (ids = {}) {
            // Розпаковуємо ID та джерело запиту
            const { productId = null, serviceId = null, source = null } = ids;
            console.log(`[Global] openGlobalFeedbackModal called. Product ID: ${productId}, Service ID: ${serviceId}, Source: ${source}`);
            if (!feedbackModal || !feedbackForm) {
                console.error('Cannot open feedback modal - elements not found.');
                return;
            }

            // Очищаємо попереднє повідомлення
            if (feedbackFormMessageContainer) feedbackFormMessageContainer.innerHTML = '';

            // --- Обробка ID Товару --- 
            let productIdInput = feedbackForm.querySelector('input[name="product_id"]');
            if (!productIdInput) {
                productIdInput = document.createElement('input');
                productIdInput.type = 'hidden';
                productIdInput.name = 'product_id';
                feedbackForm.appendChild(productIdInput);
            }
            productIdInput.value = productId || '';
            console.log('Set hidden product_id value to:', productIdInput.value);

            // --- Обробка ID Послуги --- 
            let serviceIdInput = feedbackForm.querySelector('input[name="service_id"]');
            if (!serviceIdInput) {
                serviceIdInput = document.createElement('input');
                serviceIdInput.type = 'hidden';
                serviceIdInput.name = 'service_id';
                feedbackForm.appendChild(serviceIdInput);
            }
            serviceIdInput.value = serviceId || '';
            console.log('Set hidden service_id value to:', serviceIdInput.value);
            // --- Кінець обробки ID Послуги --- 

            // --- Обробка Джерела Запиту --- 
            let sourceInput = feedbackForm.querySelector('input[name="request_source"]');
            if (!sourceInput) {
                sourceInput = document.createElement('input');
                sourceInput.type = 'hidden';
                sourceInput.name = 'request_source';
                feedbackForm.appendChild(sourceInput);
            }
            sourceInput.value = source || ''; // Встановлюємо джерело або порожній рядок
            console.log('Set hidden request_source value to:', sourceInput.value);
            // --- Кінець обробки Джерела Запиту --- 

            feedbackModal.classList.add('is-open');
            document.body.classList.add('modal-open');
            console.log('Global feedback modal opened.');
        }

        // Закриття модального вікна ФОРМИ
        const closeFeedbackModal = function () {
            console.log('[Global] Closing feedback modal.');
            feedbackModal.classList.remove('is-open');
            // Перевіряємо, чи відкрита модалка товару (якщо вона є на сторінці)
            const articleModal = document.getElementById('articleModal');
            if (!articleModal || !articleModal.classList.contains('is-open')) {
                document.body.classList.remove('modal-open');
                console.log('[Global] Removed modal-open from body.');
            }
            if (feedbackFormMessageContainer) feedbackFormMessageContainer.innerHTML = '';
            const productIdInput = feedbackForm.querySelector('input[name="product_id"]');
            if (productIdInput) {
                productIdInput.value = ''; // Очищаємо ID
            }
        };
        if (feedbackModalClose) feedbackModalClose.addEventListener('click', closeFeedbackModal);
        if (feedbackModalOverlay) feedbackModalOverlay.addEventListener('click', closeFeedbackModal);

        // Обробник для кнопки "Подзвоніть мені"
        if (callMeButton) {
            console.log('Attaching listener to Call Me button:', callMeButton);
            callMeButton.addEventListener('click', function () {
                console.log('[Global] Call Me button clicked.');
                window.openGlobalFeedbackModal(); // Викликаємо глобальну функцію без ID
            });
        } else {
            console.warn('Call Me button (.call-me-button) not found.');
        }

        // AJAX Відправка форми зворотного зв'язку
        if (feedbackForm) {
            console.log('[Global] Adding submit listener to feedback form:', feedbackForm);
            feedbackForm.addEventListener('submit', function (e) {
                e.preventDefault();
                console.log('[Global] Feedback form submitted.');
                const formData = new FormData(this);
                const actionUrl = this.getAttribute('data-action-url');

                if (!feedbackFormMessageContainer) {
                    console.error('[Global] Message container not found for feedback form.');
                    return;
                }
                feedbackFormMessageContainer.innerHTML = '<p>Відправка...</p>';

                fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                })
                    .then(response => {
                        console.log('[Global] Received response status:', response.status);
                        return response.json().then(data => ({ status: response.status, ok: response.ok, body: data }));
                    })
                    .then(result => {
                        console.log('[Global] Processed result:', result);
                        const data = result.body;
                        if (result.ok && data.status === 'success') {
                            feedbackFormMessageContainer.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                            this.reset();
                            console.log('[Global] Form reset successfully.');
                        } else if (data.status === 'error' && data.errors) {
                            let errorHtml = '<ul class="errorlist">';
                            for (const field in data.errors) {
                                errorHtml += `<li><strong>${field}:</strong> ${data.errors[field].join(', ')}</li>`;
                            }
                            errorHtml += '</ul>';
                            feedbackFormMessageContainer.innerHTML = `<div class="alert alert-error">Помилка валідації:<br>${errorHtml}</div>`;
                            console.warn('[Global] Form validation errors:', data.errors);
                        } else {
                            feedbackFormMessageContainer.innerHTML = `<div class="alert alert-error">${data.message || 'Сталася невідома помилка.'} (Статус: ${result.status})</div>`;
                            console.error('[Global] Unknown server error or unexpected response:', data);
                        }
                    })
                    .catch(error => {
                        feedbackFormMessageContainer.innerHTML = '<div class="alert alert-error">Мережева помилка або помилка відповіді сервера. Спробуйте ще раз.</div>';
                        console.error('[Global] Form submit fetch/parse error:', error);
                    });
            });
        } else {
            console.warn('[Global] Feedback form not found, submit listener not added.');
        }

        // Глобальне закриття за Escape (тільки якщо модалки існують)
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                const articleModal = document.getElementById('articleModal'); // Перевіряємо тут
                if (feedbackModal && feedbackModal.classList.contains('is-open')) {
                    closeFeedbackModal();
                } else if (articleModal && articleModal.classList.contains('is-open')) {
                    // Закриття модалки товару обробляється локально в catalog.html або іншому скрипті
                    // Тут можна було б викликати глобальну функцію закриття, якщо б вона була
                    // window.closeGlobalArticleModal(); 
                }
            }
        });
    }

    // --- Ініціалізація скриптів для конкретних сторінок --- 

    // Додаємо клас для body на контентних сторінках
    if (document.querySelector('.page-container.about-page, .content-page')) {
        document.body.classList.add('content-page');
        console.log("Detected about-page or content-page. Adding content-page class to body.");
    }

    // Додаємо обробники для карток, що перевертаються (flip-cards) на сторінці 'Про нас'
    const flipCards = document.querySelectorAll('.flip-card');
    if (flipCards.length > 0) {
        flipCards.forEach(card => {
            card.addEventListener('click', function () {
                this.classList.toggle('is-flipped');
            });
            card.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.classList.toggle('is-flipped');
                }
            });
        });
    }

    // Логіка для модального вікна ТОВАРУ (#articleModal) - перенесено з catalog.html
    const articleModal = document.getElementById('articleModal');
    if (articleModal) {
        const articleModalContent = articleModal.querySelector('.modal-full-content');
        const articleModalTitle = articleModal.querySelector('.modal-title');
        const articleModalClose = articleModal.querySelector('.article-modal-close');
        const articleModalOverlay = articleModal.querySelector('.article-modal-overlay');

        // Закриття модального вікна ТОВАРУ
        const closeArticleModal = function () {
            articleModal.classList.remove('is-open');
            const feedbackModal = document.getElementById('feedbackModal');
            if (!feedbackModal || !feedbackModal.classList.contains('is-open')) {
                document.body.classList.remove('modal-open');
            }
            if (articleModalTitle) articleModalTitle.innerHTML = '';
            if (articleModalContent) articleModalContent.innerHTML = '';
        };

        if (articleModalClose) articleModalClose.addEventListener('click', closeArticleModal);
        if (articleModalOverlay) articleModalOverlay.addEventListener('click', closeArticleModal);

        // Делегування події для кнопки "Замовити" всередині articleModal
        if (articleModalContent) {
            articleModalContent.addEventListener('click', function (e) {
                const orderButton = e.target.closest('.product-order-btn');
                if (orderButton) {
                    console.log('[Main] Order button clicked inside article modal.');
                    e.preventDefault();
                    e.stopPropagation();
                    const productId = orderButton.dataset.productId;
                    const serviceId = orderButton.dataset.serviceId; // Отримуємо ID послуги
                    // Визначаємо джерело: 'product' чи 'service'
                    const source = productId ? 'product_modal' : (serviceId ? 'service_modal' : null);

                    // Викликаємо глобальну функцію відкриття модалки форми
                    if (typeof window.openGlobalFeedbackModal === 'function') {
                        // Передаємо або productId, або serviceId, та джерело
                        window.openGlobalFeedbackModal({ productId: productId, serviceId: serviceId, source: source });
                    } else {
                        console.error('Global function openGlobalFeedbackModal is not defined!');
                    }
                }
            });
        }
    }

}); // Кінець DOMContentLoaded
