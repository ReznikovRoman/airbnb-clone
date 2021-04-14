from django.apps import AppConfig


class RealtyConfig(AppConfig):
    name = 'realty'

    def ready(self):
        from . import signals
