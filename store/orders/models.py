from django.db import models
from store.orders.enums import OrderStatusEnums
import uuid
from store.products.models import Product


class Order(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    total_price = models.FloatField()
    status = models.SmallIntegerField(
        max_length=10,
        choices=OrderStatusEnums.choices(),
        default=OrderStatusEnums.PENDING.value,
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        db_table = "orders"
        managed = True


class OrderItem(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        db_table = "order_items"
        managed = True
