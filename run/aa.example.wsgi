import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'DJANGOPROJECT.settings'

sys.path.append('/PATH/TO/PARENT/DJANGOPROJECT/')
sys.path.append('/PATH/TO/PARENT/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
