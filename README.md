# Air in UA - сайт з продажу та встановлення кондиціонерів

## Деплой на cPanel

### 1. Підготовка файлів
1. Клонуйте або завантажте проект:
   ```
   git clone https://github.com/yourusername/airinua.git
   ```

2. Переконайтеся, що всі необхідні файли присутні:
   - `passenger_wsgi.py`
   - `.htaccess` 
   - `requirements.txt`
   - `env_template.txt` (для створення `.env` на сервері)
   - коректні налаштування в `config/settings.py`

3. Видаліть зайві файли перед архівацією (запустіть скрипт `deploy.sh` або виконайте команди вручну):
   ```bash
   find . -name '.DS_Store' -delete
   find . -name '__MACOSX' -exec rm -rf {} +
   find . -name '*.pyc' -delete
   find . -name '__pycache__' -exec rm -rf {} +
   ```

4. Стягніть останні зміни та створіть архів (скрипт `deploy.sh` зробить це автоматично під назвою `airinua_deploy.zip`):
   ```bash
   zip -r airinua.zip . -x "*.git*" "*.DS_Store" "*__pycache__*" "*.pyc" "venv/*" "*.zip" "logs/*" "staticfiles/*"
   ```

### 2. Налаштування на cPanel

1. **Завантаження файлів**
   - Завантажте архів (`airinua_deploy.zip` або `airinua.zip`) на хостинг.
   - Розпакуйте архів в кореневу папку вашого сайту (наприклад, `/home/username/airinua.com`)
   - **ВАЖЛИВО:** Редагуйте `passenger_wsgi.py` на сервері, вкажіть правильний шлях до інтерпретатора Python у вашому віртуальному середовищі:
     ```python
     # Замініть на ваш реальний шлях!
     INTERP = os.path.expanduser("/home/username/airinua.com/venv/bin/python")
     ```

2. **Створіть та налаштуйте .env файл**
   - У терміналі перейдіть до папки проекту: `cd ~/airinua.com`
   - Скопіюйте шаблон: `cp env_template.txt .env`
   - Відредагуйте `.env` (`nano .env` або через файловий менеджер cPanel) та замініть:
     - `DJANGO_SECRET_KEY` (згенеруйте новий надійний ключ)
     - `DATABASE_URL` (якщо використовуєте іншу БД, наприклад PostgreSQL)
     - Всі налаштування `EMAIL_*` на ваші реальні дані Gmail або іншого провайдера.
     - `ADMIN_EMAIL` на вашу пошту адміністратора.

3. **Віртуальне середовище**
   - У терміналі cPanel (в папці проекту):
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

4. **Міграція, Статика та Суперкористувач**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser # Створіть обліковий запис адміністратора
   ```

5. **Налаштування Python App у cPanel**
   - Перейдіть до розділу "Setup Python App".
   - Створіть новий додаток або відредагуйте існуючий:
      - Application root: `/home/username/airinua.com` (шлях до вашого проекту)
      - Application URL: `airinua.com` (ваш домен)
      - Application startup file: `passenger_wsgi.py`
      - Application Entry point: `application`
      - Passenger log file: Можна залишити за замовчуванням або вказати шлях типу `/home/username/logs/passenger.log`
      - Python version: Виберіть версію, яку використовували локально (наприклад, 3.10 або 3.11).
   - **Збережіть** зміни та натисніть **Restart**.

### 3. Перевірка налаштувань

1. **Критичні перевірки**
   - Відкрийте сайт `https://airinua.com` у браузері.
   - Перевірте, чи коректно завантажуються сторінки, стилі (CSS) та зображення (медіа).
   - Спробуйте відправити заявку через форму зворотного зв'язку.
   - Зайдіть до адмін-панелі (`/admin/` або `/uaadmin/`) з даними суперкористувача.
   - Переконайтеся, що сайт працює через HTTPS.

2. **Усунення типових проблем**
   - **500 Internal Server Error:**
     - Перевірте лог Passenger: шлях вказаний у налаштуваннях Python App (або `stderr.log`).
     - Перевірте лог Django: `/home/username/airinua.com/logs/django.log`.
     - Переконайтеся, що `passenger_wsgi.py` вказує правильний шлях до `venv`.
     - Перевірте правильність змінних у `.env`.
   - **Проблеми з медіа-файлами (зображення не видно):**
     - Перевірте права доступу до папки `/home/username/airinua.com/media/` (має бути доступна для запису веб-сервером, зазвичай права 755 або 775).
     - Перевірте, чи коректно працює правило для `/media/` в `.htaccess`.
   - **Проблеми зі статикою (CSS, JS не завантажуються):**
     - Переконайтеся, що `collectstatic` було виконано.
     - Перевірте, чи існує папка `/home/username/airinua.com/staticfiles/` і чи вона містить файли.
     - Перевірте налаштування `STATICFILES_STORAGE` та `WhiteNoiseMiddleware` в `settings.py`.
     - Спробуйте розкоментувати правило для `/static/` в `.htaccess`, якщо WhiteNoise з якихось причин не працює.
   - **Сторінка не знайдена (404):**
     - Перевірте `config/urls.py` та `airinua/urls.py`.

### 4. Додаткові оптимізації

1. **Кешування:** Переконайтесь, що налаштування кешування в `.htaccess` активні.
2. **Безпека:**
   - Використовуйте надійний `SECRET_KEY` у `.env`.
   - `DEBUG = False` та `SECURE_SSL_REDIRECT = True` в `settings.py` для продакшену.

### Корисні команди для cPanel (у терміналі)

- Перезапуск Python додатку (якщо `touch` не працює, використовуйте кнопку Restart у cPanel):
  ```bash
  touch ~/airinua.com/tmp/restart.txt
  ```
- Перегляд логу Passenger:
  ```bash
  tail -f ~/logs/passenger.log # Або інший шлях, вказаний у налаштуваннях
  ```
- Перегляд логу Django:
  ```bash
  tail -f ~/airinua.com/logs/django.log
  ```

## Контактна інформація

- Веб-сайт: [airinua.com](https://airinua.com)
- Email: support@airinua.com
