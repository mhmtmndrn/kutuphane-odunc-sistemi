"""Catalog routes (plan §4.1)."""

from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("kitaplar/", views.book_search, name="search"),
    path("kitaplar/yeni/", views.book_create, name="create"),
    path("kitaplar/<int:pk>/", views.book_detail, name="detail"),
    path("kitaplar/<int:pk>/duzenle/", views.book_edit, name="edit"),
    path("kitaplar/<int:pk>/nusha/", views.book_add_copies, name="add-copies"),
]
