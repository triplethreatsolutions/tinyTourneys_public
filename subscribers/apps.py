from django.apps import AppConfig


class SubscribersConfig(AppConfig):
    name = "subscribers"

    def ready(self):
        # This import is required when using the @receiver decorator
        from subscribers import signals
