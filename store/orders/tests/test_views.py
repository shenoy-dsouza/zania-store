from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from store.orders.models import Order, OrderItem
from store.products.tests.factories import ProductsFactory
from unittest.mock import patch
from rest_framework.serializers import ValidationError


class TestOrderCreateAPIView(APITestCase):
    def setUp(self):
        self.url = reverse("order:list-create")
        self.product = ProductsFactory(
            name="Test Product", stock=10, price=20.0
        )  # Create a sample product

    def test_get_orders_empty_list(self):
        """Test fetching orders when no orders exist."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 0
        assert response.json()["data"] == []

    def test_create_order_success(self):
        """Test successfully creating an order."""
        payload = {"products": [{"product_id": str(self.product.id), "quantity": 2}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "success"
        assert response.json()["total_price"] == 40.0
        assert Order.objects.count() == 1
        created_order = OrderItem.objects.filter(product=self.product).first()
        assert created_order.quantity == 2
        assert created_order.order.total_price == 40

    def test_create_order_invalid_product(self):
        """Test creating an order with an invalid product ID."""
        payload = {"products": [{"product_id": "99999999", "quantity": 1}]}
        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "product_id" in response.json()["errors"]["products"][0]

    def test_create_order_insufficient_stock(self):
        """Test creating an order when stock is insufficient."""
        payload = {"products": [{"product_id": str(self.product.id), "quantity": 100}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "stock" in response.json()["errors"]

    def test_create_order_negative_quantity(self):
        """Test ordering a product with negative quantity."""
        payload = {"products": [{"product_id": str(self.product.id), "quantity": -2}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_zero_quantity(self):
        """Test ordering a product with zero quantity."""
        payload = {"products": [{"product_id": str(self.product.id), "quantity": 0}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_empty_product_list(self):
        """Test creating an order with an empty product list."""
        payload = {"products": []}
        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_missing_products_key(self):
        """Test creating an order without the 'products' key."""
        payload = {}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_invalid_product_id_format(self):
        """Test creating an order with an invalid product_id format."""
        payload = {"products": [{"product_id": "invalid-uuid", "quantity": 1}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_max_stock(self):
        """Test ordering the exact available stock."""
        product = ProductsFactory(stock=50, price=20.0)

        payload = {"products": [{"product_id": str(product.id), "quantity": 50}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        self.product.refresh_from_db()
        assert product.stock == 50  # Stock should be depleted

    def test_create_order_multiple_products(self):
        """Test creating an order with multiple products."""
        product2 = ProductsFactory(stock=5, price=15.0)
        payload = {
            "products": [
                {"product_id": str(self.product.id), "quantity": 2},
                {"product_id": str(product2.id), "quantity": 1},
            ]
        }
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["total_price"] == 55.0  # (2x20) + (1x15)
        assert Order.objects.count() == 1

        created_order = OrderItem.objects.filter(product=self.product).first()
        assert created_order.quantity == 2

        created_order = OrderItem.objects.filter(product=product2).first()
        assert created_order.quantity == 1

        assert created_order.order.total_price == 55

    def test_create_order_total_price_calculation(self):
        """Test correct total price calculation."""
        payload = {"products": [{"product_id": str(self.product.id), "quantity": 3}]}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["total_price"] == 60.0  # 3 * 20

    @patch("store.orders.utils.order_processing.process_order")
    def test_create_order_concurrent_stock_update(self, mock_process_order):
        """Test concurrent order processing where stock runs out."""
        mock_process_order.side_effect = [
            Order.objects.create(total_price=20),
            ValidationError("Stock error"),
        ]

        payload = {"products": [{"product_id": str(self.product.id), "quantity": 10}]}
        response1 = self.client.post(self.url, payload, format="json")
        response2 = self.client.post(self.url, payload, format="json")

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response2.json()["errors"]["stock"]
            == f"Not enough stock for {self.product.name}. Available: 0, Requested: 10"
        )
        assert "stock" in str(response2.json()["errors"])
