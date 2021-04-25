from django.http import Http404

from django_policies.filters import conjunct


class FilterQuerysetMixin:

    def _get_filter(self):
        filters = set(
            perm.get_filter(self.request, self)
            for perm in self.get_permissions()
            if hasattr(perm, "get_filter")
        )
        return conjunct(filters)

    def filter_queryset(self, queryset):
        filter = self._get_filter()
        return super().filter_queryset(
            queryset.filter(filter)
        )


class ObjectPermissionMixin:
    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                raise Http404
