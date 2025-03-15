from rest_framework import serializers
from store.products.models import Product


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id", "created"]  # Make these fields read-only

    def validate_name(self, value):
        """Ensure the product name is a string and not a number."""
        if not isinstance(value, str):
            raise serializers.ValidationError("Product name must be a string.")
        if value.isdigit():
            raise serializers.ValidationError(
                "Product name cannot be entirely numeric."
            )
        if Product.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "A product with this name already exists."
            )
        return value
