from django.apps import AppConfig


class DjangoPDFOverlayConfig(AppConfig):
    name = 'django_pdf_overlay'

    def ready(self):
        from . import signals  # noqa, flake8 issue
