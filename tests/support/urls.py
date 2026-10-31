"""Test-only URLconf (plan §11, G02 (a)).

``/odunc/`` belongs to G11. Until then the session and login tests need a
staff page, so this URLconf adds a stand-in view next to the real routes.
Product code carries no placeholder.
"""

from django.http import HttpRequest, HttpResponse
from django.urls import path

from accounts.permissions import staff_view
from library_site.urls import urlpatterns as product_urlpatterns


@staff_view
def checkout_stand_in(request: HttpRequest) -> HttpResponse:
    return HttpResponse("odunc")


urlpatterns = [
    *product_urlpatterns,
    path("odunc/", checkout_stand_in, name="checkout-stand-in"),
]
