from django.contrib.auth.backends import AllowAllUsersModelBackend

from .filters import QNone
from .registry import policies


class Backend(AllowAllUsersModelBackend):
    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if not hasattr(user_obj, "_perm_cache"):
            user_obj._perm_cache = {
                *self.get_user_permissions(user_obj),
                *self.get_group_permissions(user_obj),
            }
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            return super().has_perm(user_obj, perm, obj=None)
        return (
            super().has_perm(user_obj, perm, obj=None)
            and policies.has_perm(user_obj, perm, obj)
        )

    def get_filter(self, user_obj, perm_list):
        if not all(self.has_perm(user_obj, perm) for perm in perm_list):
            return QNone
        return policies.get_filter(user_obj, perm_list)
