import os
import sys

    
INTERP = os.path.expanduser("/home3/airinuac/virtualenv/public_html/climat/3.9/bin/python")

if sys.executable != INTERP:
   try:
       os.execl(INTERP, INTERP, *sys.argv)
   except OSError:
       pass # Continue execution with the current interpreter

# Додаємо шлях до кореневої папки проекту
sys.path.insert(0, '/home3/airinuac/public_html/climat')

# Вказуємо Django, де знаходяться налаштування
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Імпортуємо та запускаємо WSGI додаток Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
