import os
import sys

path = 'C:\Users\Gabriel Higor\Documents\Projeto Gym.app\Olympus'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
