from .exceptions import PolicyAlreadyRegistered, PolicyNotRegistered
from .filters import conjunct
from .utils import get_permission


class Policies:
    def __init__(self):
        self._registry = {}

    def register(self, model, *actions):
        def _register(cls):
            for action in actions:
                perm = get_permission(action, model._meta)
                if perm in self._registry:
                    raise PolicyAlreadyRegistered(perm)
                self._registry[perm] = cls()
            return cls
        return _register

    def get_policy(self, perm):
        if perm not in self._registry:
            raise PolicyNotRegistered(perm)
        return self._registry[perm]

    def get_policies(self, perm_list):
        for perm_name in perm_list:
            try:
                yield self.get_policy(perm_name)
            except PolicyNotRegistered:
                pass

    def has_perm(self, user_obj, perm, obj):
        try:
            policy = self.get_policy(perm)
        except PolicyNotRegistered:
            return True

        return policy.has_perm_final(user_obj, obj)

    def get_filter(self, user_obj, perm_list):
        filters = set(
            policy.get_filter_final(user_obj)
            for policy in self.get_policies(perm_list)
        )
        return conjunct(filters)


policies = Policies()
