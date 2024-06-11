"""
WSGI config for storeinv project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application



application = get_wsgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeinv.settings')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'storeinv.settings'

## Uncomment the lines below depending on your Django version
###### then, for Django >=1.5:
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
