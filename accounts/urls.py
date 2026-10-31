"""Accounts routes (plan §4.1)."""

from django.urls import path

from . import views

urlpatterns = [
    path("giris/", views.LoginView.as_view(), name="login"),
    path("cikis/", views.LogoutView.as_view(), name="logout"),
]
