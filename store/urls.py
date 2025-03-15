from django.contrib import admin
from django.urls import path
from django.views import defaults as default_views
from django.urls import include

urlpatterns = [
    path(
        "",
        default_views.permission_denied,
        kwargs={"exception": Exception("Permission Denied")},
        name="home",
    ),
    path(
        "orders",
        include("store.orders.urls", namespace="order"),
    ),
    path(
        "products",
        include("store.products.urls", namespace="products"),
    ),
]
