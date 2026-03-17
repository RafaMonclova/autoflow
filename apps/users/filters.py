from django_filters import rest_framework as filters
from django.db.models import Q

from .models import (
    User
)


class UserFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_by_all_fields')
    is_active = filters.BooleanFilter(field_name='is_active')
    role = filters.NumberFilter(field_name='role__id')

    class Meta:
        model = User
        fields = ['name', 'is_active', 'role']

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )
