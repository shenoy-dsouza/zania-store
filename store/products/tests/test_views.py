from django.urls import reverse
from store.products.models import Product
from rest_framework import status
from rest_framework.test import APITestCase
from store.products.tests.factories import ProductsFactory


class TestProductListCreateAPIView(APITestCase):
    def setUp(self):
        self.url = reverse(
            "products:list-create"
        )  # Ensure the URL name matches your Django URLs

    def test_get_products_empty_list(self):
        """Test fetching products when no products exist."""
        response = self.client.get(
            self.url,
            {},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_get_products_with_data(self):
        """Test fetching products when products exist."""
        ProductsFactory.create_batch(4)

        response = self.client.get(
            self.url,
            {},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 4

    def test_get_products_with_filter(self):
        """Test filtering products by name."""
        ProductsFactory.create(name="Laptop")
        ProductsFactory.create(name="mouse")

        response = self.client.get(
            self.url,
            {"name": "laptop"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 1
        assert response.json()["data"][0]["name"] == "Laptop"

    def test_get_products_with_nonexistent_filter(self):
        """Test filtering products by a name that does not exist."""
        ProductsFactory.create(name="Laptop")

        response = self.client.get(self.url, {"name": "Tablet"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 0

    def test_get_products_with_ordering(self):
        """Test ordering products by name."""
        ProductsFactory.create(name="mobile")
        ProductsFactory.create(name="earphone")

        # test with name ascending
        response = self.client.get(
            self.url,
            {"ordering": "name"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 2
        assert response.json()["data"][0]["name"] == "earphone"
        assert response.json()["data"][1]["name"] == "mobile"

        # test with name descending
        response = self.client.get(
            self.url,
            {"ordering": "-name"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["count"] == 2
        assert response.json()["data"][0]["name"] == "mobile"
        assert response.json()["data"][1]["name"] == "earphone"

    def test_create_product_success(self):
        """Test successfully creating a new product."""
        data = {
            "name": "keyboard",
            "description": "Mechanical keyboard",
            "price": 75.5,
            "stock": 20,
        }
        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"
        assert response.data["data"]["name"] == "keyboard"

        product = Product.objects.get(name="keyboard")
        assert product.description == "Mechanical keyboard"
        assert product.price == 75.5
        assert product.stock == 20

    def test_create_product_missing_fields(self):
        """Test creating a product with missing required fields."""
        data = {"description": "Mechanical keyboard", "price": 75.5, "stock": 20}
        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data["errors"]

    def test_create_product_duplicate(self):
        """Test creating a duplicate product (should fail validation)."""
        ProductsFactory.create(name="monitor")

        data = {
            "name": "monitor",
            "description": "some description for monitor",
            "price": 50,
            "stock": 20,
        }
        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data["errors"]
        assert (
            response.data["errors"]["name"][0]
            == "A product with this name already exists."
        )

    def test_create_product_name_numeric(self):
        """Test creating a product name with numeric"""

        data = {
            "name": 123,
            "description": "some description for 123",
            "price": 50,
            "stock": 20,
        }
        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data["errors"]
        assert (
            response.data["errors"]["name"][0]
            == "Product name cannot be entirely numeric."
        )

    def test_create_product_negative_values(self):
        """Test creating a product with negative price or stock should fail."""
        data = {
            "name": "Test Product",
            "description": "Some description",
            "price": -10,
            "stock": -5,
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data["errors"]
        assert "stock" in response.data["errors"]

    def test_create_product_zero_values(self):
        """Test creating a product with zero price and stock."""
        data = {
            "name": "Test Product",
            "description": "Zero stock and price",
            "price": 0,
            "stock": 0,
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data["errors"]
        assert "stock" in response.data["errors"]

    def test_create_product_missing_description(self):
        """Test creating a product without a description."""
        data = {"name": "No Description", "price": 50, "stock": 10}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "description" in response.data["errors"]

    def test_create_product_long_name(self):
        """Test creating a product with a very long name."""
        long_name = "A" * 101  # 101 characters (exceeds max_length=100)
        data = {
            "name": long_name,
            "description": "Too long name",
            "price": 100,
            "stock": 5,
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data["errors"]
