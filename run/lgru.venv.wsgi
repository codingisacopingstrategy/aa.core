import os
import sys
import site 


sys.stdout = sys.stderr


ALLDIRS = ['/var/www/vhosts/aa.lgru.net/venv/lib/python2.6/site-packages/']


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


os.environ['DJANGO_SETTINGS_MODULE'] = 'run.settings'

sys.path.append('/var/www/vhosts/aa.lgru.net/aa.core/run/')
sys.path.append('/var/www/vhosts/aa.lgru.net/aa.core/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
