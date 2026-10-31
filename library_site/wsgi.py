"""WSGI entry point, served by waitress (ADR-0012)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_site.settings.prod")

application = get_wsgi_application()
