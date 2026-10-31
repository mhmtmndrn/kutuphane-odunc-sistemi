"""Accounts routes (plan §4.1)."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("giris/", views.LoginView.as_view(), name="login"),
    path("cikis/", views.LogoutView.as_view(), name="logout"),
    path("parola/", views.password_change, name="password-change"),
    path("personel/", views.staff_list, name="staff-list"),
    path("personel/yeni/", views.staff_create, name="staff-create"),
    path("personel/<int:pk>/", views.staff_detail, name="staff-detail"),
    path("personel/<int:pk>/pasif/", views.staff_deactivate, name="staff-deactivate"),
    path("personel/<int:pk>/parola/", views.staff_reset_password, name="staff-reset-password"),
    path("personel/<int:pk>/kilit-ac/", views.staff_unlock, name="staff-unlock"),
]
