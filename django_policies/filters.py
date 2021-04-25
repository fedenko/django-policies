import operator
from functools import reduce

from django.db.models import Q

QNone = Q(pk__in=[])
QAll = ~QNone


def conjunct(filters):
    _filters = set(filters)
    if len(_filters) == 0:
        return QAll
    if len(_filters) == 1:
        return next(iter(_filters))

    return reduce(operator.and_, _filters)
