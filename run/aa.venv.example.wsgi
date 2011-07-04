import os
import sys
import site 


ALLDIRS = ['/PATH/TO/YOUR/venv/lib/pythonX.X/site-packages/']


# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 


os.environ['DJANGO_SETTINGS_MODULE'] = 'DJANGOPROJECT.settings'

sys.path.append('/PATH/TO/PARENT/DJANGOPROJECT/')
sys.path.append('/PATH/TO/PARENT/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
