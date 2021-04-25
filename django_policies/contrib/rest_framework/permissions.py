"""
Provides a set of pluggable permission policies.
"""
from rest_framework import exceptions

from django_policies.filters import QAll


class OperationHolderMixin:
    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)


class SingleOperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class
        if not (
            isinstance(self.op1_class, self.__class__)
            or hasattr(self.op1_class, "get_filter")
        ):
            raise TypeError(
                "Bitwise operators is not supported for {}".format(
                    self.op1_class
                )
            )
        if not (
            isinstance(self.op2_class, self.__class__)
            or hasattr(self.op2_class, "get_filter")
        ):
            raise TypeError(
                "Bitwise operators is not supported for {}".format(
                    self.op2_class
                )
            )

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, view):
        return self.op1.has_permission(
            request, view
        ) and self.op2.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self.op1.has_object_permission(
            request, view, obj
        ) and self.op2.has_object_permission(request, view, obj)

    def get_filter(self, request, view):
        return self.op1.get_filter(request, view) & self.op2.get_filter(
            request, view
        )


class OR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, view):
        return self.op1.has_permission(
            request, view
        ) or self.op2.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self.op1.has_object_permission(
            request, view, obj
        ) or self.op2.has_object_permission(request, view, obj)

    def get_filter(self, request, view):
        return self.op1.get_filter(request, view) | self.op2.get_filter(
            request, view
        )


class NOT:
    def __init__(self, op1):
        self.op1 = op1

    def has_permission(self, request, view):
        return not self.op1.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return not self.op1.has_object_permission(request, view, obj)

    def get_filter(self, request, view):
        return ~self.op1.get_filter(request, view)


class BasePermissionMetaclass(OperationHolderMixin, type):
    pass


class BasePermission(metaclass=BasePermissionMetaclass):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def get_filter(self, request, view):
        return QAll


class ObjectPermissions(BasePermission):
    GET = ["%(app_label)s.view_%(model_name)s"]
    OPTIONS = []
    HEAD = []
    POST = ["%(app_label)s.add_%(model_name)s"]
    PUT = ["%(app_label)s.change_%(model_name)s"]
    PATCH = PUT
    DELETE = ["%(app_label)s.delete_%(model_name)s"]

    @property
    def perms_map(self):
        return {
            "GET": self.GET,
            "OPTIONS": self.OPTIONS,
            "HEAD": self.HEAD,
            "POST": self.POST,
            "PUT": self.PUT,
            "PATCH": self.PATCH,
            "DELETE": self.DELETE,
        }

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            "app_label": model_cls._meta.app_label,
            "model_name": model_cls._meta.model_name,
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _queryset(self, view):
        assert (
            hasattr(view, "get_queryset")
            or getattr(view, "queryset", None) is not None
        ), (
            "Cannot apply {} on a view that does not set "
            "`.queryset` or have a `.get_queryset()` method."
        ).format(
            self.__class__.__name__
        )

        if hasattr(view, "get_queryset"):
            queryset = view.get_queryset()
            assert (
                queryset is not None
            ), "{}.get_queryset() returned None".format(
                view.__class__.__name__
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not (request.user and request.user.is_authenticated):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return request.user.has_perms(perms)

    def has_object_permission(self, request, view, obj):
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            return False

        return True

    def get_filter(self, request, view):
        queryset = self._queryset(view)
        model_cls = queryset.model

        perms = self.get_required_permissions(request.method, model_cls)
        return request.user.get_filter(perms)
