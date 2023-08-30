from django.apps import AppConfig


class RaffleshopAppConfig(AppConfig):
    name = 'raffleshop'

    def ready(self):
        import raffleshop.signals
