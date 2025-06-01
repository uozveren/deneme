from django.apps import AppConfig


class FrontendConfig(AppConfig):
    name = 'frontend'

    def ready(self):
        # Import signals to ensure they are registered
        from . import signals  # noqa
