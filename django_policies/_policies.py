from .filters import QAll, QNone


class Policy:
    QNone = QNone
    QAll = QAll

    def has_perm_final(self, user_obj, obj):
        if user_obj.is_superuser:
            return True
        return self.has_perm(user_obj, obj)

    def has_perm(self, user_obj, obj):
        return False

    def get_filter_final(self, user_obj):
        if user_obj.is_superuser:
            return self.QAll
        return self.get_filter(user_obj)

    def get_filter(self, user_obj):
        return self.QNone
