from django.apps import AppConfig


class DjangoPDFOverlayConfig(AppConfig):
    name = 'django_pdf_overlay'
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import signals  # noqa, flake8 issue
