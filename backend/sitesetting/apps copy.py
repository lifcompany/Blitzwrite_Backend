import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SitesettingConfig(AppConfig):
    name = "backend.sitesetting"
    verbose_name = _("Sitesetting")

    def ready(self):
        with contextlib.suppress(ImportError):
            import backend.sitesetting.signals  # noqa: F401
