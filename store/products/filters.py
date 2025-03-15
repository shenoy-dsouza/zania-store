from store.products.models import Product
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Product
        fields = ["name"]
