from django.apps import AppConfig


class DjangoPDFFillerConfig(AppConfig):
    name = 'django_pdf_filler'

    def ready(self):
        from . import signals  # noqa, flake8 issue
