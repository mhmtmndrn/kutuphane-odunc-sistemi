"""WSGI entry point, served by waitress (ADR-0012).

After the application is loaded the process takes the application lock on
``<LIBRARY_DB_PATH>.app.lock`` and keeps it for its whole life (KL-4, R-09):
a second process on the same database stops here with
``RuntimeError("Uygulama zaten çalışıyor: <kilit yolu>")`` and
``restore_backup`` refuses to run. Then, if ``LIBRARY_SCHEDULER_ENABLED`` is
"1", the in-process scheduler starts (KL-5, ADR-0007). Tests and management
commands do not import this module.
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_site.settings.prod")

application = get_wsgi_application()

from django.conf import settings  # noqa: E402

from operations.applock import hold_app_lock  # noqa: E402

# Referenced for the life of the process; closing it would free the lock.
_app_lock = hold_app_lock(Path(settings.DATABASES["default"]["NAME"]))

if settings.LIBRARY_SCHEDULER_ENABLED == "1":
    from operations.scheduler import start_scheduler

    start_scheduler()
