from django.urls import path
from store.orders.views import (
    OrderListCreateAPIView,
)

app_name = "orders"

urlpatterns = [
    path(
        "",
        view=OrderListCreateAPIView.as_view(),
        name="list-create",
    ),
]
