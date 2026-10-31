"""Ledger routes (plan §4.1)."""

from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("borclar/<int:member_no>/", views.statement, name="statement"),
    path("borclar/<int:member_no>/odeme/", views.payment, name="payment"),
    path("borclar/<int:member_no>/af/", views.waiver, name="waiver"),
    path("borclar/<int:member_no>/para-iadesi/", views.refund, name="refund"),
    path("borclar/<int:member_no>/iptal/", views.cancel, name="cancel"),
]
