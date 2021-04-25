from django.contrib.admin import RelatedFieldListFilter

from .utils import get_permission


class ObjectPermissionsRelatedFieldListFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        opts = field.related_model._meta
        filter = request.user.get_filter(
            [get_permission("view", opts)]
        ) | request.user.get_filter(
            [get_permission("change", opts)]
        )
        return field.get_choices(include_blank=False, limit_choices_to=filter)


class ObjectPermissionsMixin:

    def _is_changelist(self, request):
        opts = self.opts
        return request.resolver_match.url_name == "{}_{}_changelist".format(
            opts.app_label, opts.model_name
        )

    def _get_permission(self, action):
        return get_permission(action, self.opts)

    def _get_queryset(self, request):
        return super().get_queryset(request)

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            self._get_permission("change"), obj
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm(
            self._get_permission("delete"), obj
        )

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm(
            self._get_permission("view"), obj
        ) or request.user.has_perm(
            self._get_permission("change"), obj
        )

    def get_queryset(self, request):
        if self._is_changelist(request):
            return self.get_changelist_queryset(request)
        return self._get_queryset(request)

    def get_changelist_filter(self, request):
        return request.user.get_filter(
            [self._get_permission("view")]
        ) | request.user.get_filter(
            [self._get_permission("change")]
        )

    def get_changelist_queryset(self, request):
        queryset = self._get_queryset(request)
        filter = self.get_changelist_filter(request)
        return queryset.filter(filter)

    def get_field_filter(self, request, opts):
        return request.user.get_filter(
            [get_permission("view", opts)]
        ) | request.user.get_filter(
            [get_permission("change", opts)]
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        filter = self.get_field_filter(
            request, db_field.remote_field.model._meta
        )
        kwargs.update({"limit_choices_to": filter})
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        filter = self.get_field_filter(
            request, db_field.remote_field.model._meta
        )
        kwargs.update({"limit_choices_to": filter})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
