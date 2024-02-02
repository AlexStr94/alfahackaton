from django_filters import rest_framework as filters

from iprs.models import Task


class TaskFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    status = filters.ChoiceFilter(choices=Task.STATUS_CHOICES)

    class Meta:
        model = Task
        fields = ['start_date', 'end_date', 'status']

