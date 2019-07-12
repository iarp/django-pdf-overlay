from django.apps import AppConfig


class FormsConfig(AppConfig):
    name = 'forms'

    def ready(self):
        from . import signals
