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
]
