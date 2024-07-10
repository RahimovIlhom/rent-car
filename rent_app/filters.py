import django_filters
from django_filters import rest_framework as filters
from .models import PaymentSchedule


class PaymentScheduleFilter(filters.FilterSet):
    rent_type = django_filters.CharFilter(field_name='rental__rent_type')
    year = django_filters.NumberFilter(method='filter_payment_date_year')
    month = django_filters.NumberFilter(method='filter_payment_date_month')
    day = django_filters.NumberFilter(method='filter_payment_date_day')

    class Meta:
        model = PaymentSchedule
        fields = ['rent_type', 'year', 'month', 'day']

    def filter_payment_date_year(self, queryset, name, value):
        if value:
            queryset = queryset.filter(payment_date__year=value)
        return queryset

    def filter_payment_date_month(self, queryset, name, value):
        if value:
            queryset = queryset.filter(payment_date__month=value)
        return queryset

    def filter_payment_date_day(self, queryset, name, value):
        if value:
            queryset = queryset.filter(payment_date__day=value)
        return queryset
