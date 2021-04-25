from django.apps import AppConfig


class PoliciesConfig(AppConfig):
    name = "django_policies"

    def ready(self):
        super().ready()
        self.module.autodiscover()
