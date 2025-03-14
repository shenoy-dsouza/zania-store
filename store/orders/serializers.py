from rest_framework import serializers
from store.orders.models import Order, OrderItem
from store.products.models import Product
from store.orders.enums import OrderStatusEnums

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)  # Ensure quantity is at least 1

    class Meta:
        model = OrderItem
        fields = ["product_id", "quantity"]

    def validate_product_id(self, value):
        """Ensure the product exists in the database."""
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid product_id: Product does not exist.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ["id", "products", "total_price", "status", "created"]
        read_only_fields = ["id", "total_price", "status", "created"]


    def to_representation(self, instance):
        """Customize the output representation of an order."""
        representation = super().to_representation(instance)
        
        # Fetch order items and include product details in response
        order_items = OrderItem.objects.filter(order=instance).select_related("product")

        representation["products"] = [
            {
                "product_id": str(item.product.id),
                "name": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "status": OrderStatusEnums.get_name(
                    item.order.status).lower(),
            }
            for item in order_items
        ]
        

        return representation
