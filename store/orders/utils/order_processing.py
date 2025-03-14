from django.db import transaction
from rest_framework.exceptions import ValidationError
from store.products.models import Product
from store.orders.models import Order, OrderItem
from store.orders.enums import OrderStatusEnums

def process_order(products):
    """Creates an order, validates stock, deducts inventory, and saves order items."""
    order_items = []
    total_price = 0

    with transaction.atomic():
        for item in products:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise ValidationError({"product_id": f"Product with ID {product_id} not found."})

            # **Check Stock Availability**
            if product.stock < quantity:
                raise ValidationError(
                    {"stock": f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {quantity}"}
                )

            # Deduct Stock
            product.stock -= quantity
            product.save()

            # Calculate Total Price
            total_price += product.price * quantity

            order_items.append(OrderItem(product=product, quantity=quantity))

        # Create the Order
        order = Order.objects.create(total_price=total_price, status=OrderStatusEnums.PENDING.value)

        # Save Order Items
        for item in order_items:
            item.order = order
            item.save()

        order.status = OrderStatusEnums.COMPLETED.value
        order.save()

    return order
