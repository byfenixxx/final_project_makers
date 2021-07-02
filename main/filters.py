import django_filters
from django_filters.rest_framework import FilterSet

from .models import Book


class BookFilter(FilterSet):
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    genre = django_filters.CharFilter(field_name="genre__name", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ("author", "genre")
