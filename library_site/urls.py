"""Root URL configuration (plan §4.1)."""

from django.conf import settings
from django.urls import URLPattern, URLResolver, path

urlpatterns: list[URLPattern | URLResolver] = []

# The admin panel exists only where the app is installed: dev settings
# (ADR-0024). In production /admin/ is unrouted and returns 404.
if "django.contrib.admin" in settings.INSTALLED_APPS:
    from django.contrib import admin

    urlpatterns.append(path("admin/", admin.site.urls))
