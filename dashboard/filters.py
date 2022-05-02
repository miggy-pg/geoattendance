import django_filters

from user.models import User


class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = "__all__"
