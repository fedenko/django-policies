from django.utils.module_loading import autodiscover_modules

from ._policies import Policy
from .registry import policies
from .utils import user_get_filter

__version__ = "0.1.0"

__all__ = [
    "Policy",
    "policies",
    "user_get_filter"
]


def autodiscover():
    autodiscover_modules("policies", register_to=policies)


default_app_config = "django_policies.apps.PoliciesConfig"
