"""Member routes (plan §4.1)."""

from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("uyeler/", views.member_search, name="search"),
    path("uyeler/yeni/", views.member_create, name="create"),
    path("uyeler/kart/", views.card_print, name="cards"),
    path("uyeler/<int:member_no>/", views.member_detail, name="detail"),
    path("uyeler/<int:member_no>/duzenle/", views.member_edit, name="edit"),
    path("uyeler/<int:member_no>/aktif/", views.member_reactivate, name="reactivate"),
    path("uyeler/<int:member_no>/riza/", views.member_consent, name="consent"),
]
