from django.db import transaction
from rest_framework.exceptions import ValidationError
from store.products.models import Product
from store.orders.models import Order, OrderItem
from store.orders.enums import OrderStatusEnums


def process_order(products):
    """Creates an order, validates stock, deducts inventory, and saves order items efficiently."""

    product_ids = [item["product_id"] for item in products]
    product_map = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

    order_items = []
    total_price = 0

    with transaction.atomic():
        for item in products:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            product = product_map.get(product_id)
            if not product:
                raise ValidationError(
                    {"product_id": f"Product with ID {product_id} not found."}
                )

            # **Check Stock Availability**
            if product.stock < quantity:
                raise ValidationError(
                    {
                        "stock": f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {quantity}"
                    }
                )

            # Deduct Stock
            product.stock -= quantity
            total_price += product.price * quantity

            order_items.append(OrderItem(product=product, quantity=quantity))

        # **Bulk Update Stock**
        Product.objects.bulk_update(product_map.values(), ["stock"])

        # **Create the Order**
        order = Order.objects.create(
            total_price=total_price, status=OrderStatusEnums.PENDING.value
        )

        # **Bulk Create Order Items**
        for item in order_items:
            item.order = order
        OrderItem.objects.bulk_create(order_items)

        # **Mark Order as Completed**
        order.status = OrderStatusEnums.COMPLETED.value
        order.save(update_fields=["status"])

    return order
