"""Test-only URLconf (plan §11, G02 (a)).

Until G11 this added a stand-in ``/odunc/`` view for the session and login
tests. The real checkout screen now serves that route (plan §11, G11), so the
URLconf is the product's own; the tests keep their ``@pytest.mark.urls``
marker unchanged.
"""

from library_site.urls import urlpatterns  # noqa: F401
