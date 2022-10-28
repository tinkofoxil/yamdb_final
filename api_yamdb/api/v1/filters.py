from django_filters import rest_framework as filters
from reviews.models import Title


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name="category__slug", lookup_expr="icontains"
    )
    genre = filters.CharFilter(
        field_name="genre__slug", lookup_expr="icontains"
    )
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    year = NumberInFilter(field_name="year", lookup_expr="in")

    class Meta:
        model = Title
        fields = "__all__"
