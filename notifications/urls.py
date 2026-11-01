"""Overdue list and manual reminders (plan §4.1)."""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("gecikenler/", views.overdue_list, name="overdue"),
    path("gecikenler/hatirlat/", views.remind, name="remind"),
]
