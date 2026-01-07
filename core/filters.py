import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="subcategory__category__slug",
        lookup_expr="iexact"
    )

    subcategory = django_filters.CharFilter(
        field_name="subcategory__slug",
        lookup_expr="iexact"
    )

    brand = django_filters.CharFilter(
        field_name="brand__slug",
        lookup_expr="iexact"
    )

    class Meta:
        model = Product
        fields = ["category", "subcategory", "brand"]
