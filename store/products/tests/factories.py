from store.products.models import Product
from factory.django import DjangoModelFactory


class ProductsFactory(DjangoModelFactory):
    stock = 10
    price = 100

    class Meta:
        model = Product
