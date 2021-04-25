from django.contrib import auth

from .filters import QNone, conjunct


def get_permission(action, opts):
    codename = auth.get_permission_codename(action, opts)
    return "{}.{}".format(opts.app_label, codename)


def user_get_filter(user_obj, perm_list):
    if not user_obj.has_perms(perm_list):
        return QNone
    filters = set(
        backend.get_filter(user_obj, perm_list)
        for backend in auth.get_backends() if hasattr(backend, "get_filter")
    )
    return conjunct(filters)
