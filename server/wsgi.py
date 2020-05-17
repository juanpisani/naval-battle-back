"""
WSGI config for server naval-battle-back.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = get_wsgi_application()

sys.path.append('/home/django_projects/MyProject')
sys.path.append('/home/django_projects/MyProject/myproject')
