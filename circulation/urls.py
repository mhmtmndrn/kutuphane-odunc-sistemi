"""Circulation routes (plan §4.1).

``library_site/urls.py`` includes these after ``catalog.urls``, so that
``nushalar/etiket/`` is not read as ``nushalar/<str:barcode>/`` (G08, G12).
"""

from django.urls import path

from . import views

app_name = "circulation"

urlpatterns = [
    path("odunc/", views.checkout, name="checkout"),
    path("odunc/<int:loan_id>/uzat/", views.renew, name="renew"),
    path("iade/", views.checkin, name="checkin"),
    path("nushalar/<str:barcode>/", views.copy_detail, name="copy"),
    path("nushalar/<str:barcode>/kayip/", views.copy_lost, name="copy-lost"),
    path("nushalar/<str:barcode>/hasarli/", views.copy_damaged, name="copy-damaged"),
    path("nushalar/<str:barcode>/bulundu/", views.copy_found, name="copy-found"),
    path("nushalar/<str:barcode>/onarildi/", views.copy_repaired, name="copy-repaired"),
    path("nushalar/<str:barcode>/kayittan-dus/", views.copy_withdraw, name="copy-withdraw"),
]
