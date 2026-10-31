"""Administration routes (plan §4.1)."""

from django.urls import path

from . import views

app_name = "administration"

urlpatterns = [
    path("", views.home, name="home"),
    path("ayarlar/", views.settings_view, name="settings"),
    path("kapali-gunler/", views.closed_days, name="closed-days"),
    path("kapali-gunler/tarih/", views.closed_date_add, name="closed-date-add"),
    path("kapali-gunler/tarih/<int:pk>/sil/", views.closed_date_remove, name="closed-date-remove"),
    path("denetim/", views.audit_list, name="audit"),
]
