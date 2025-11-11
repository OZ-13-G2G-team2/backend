from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from app.carts.models import Cart, CartItem
from unittest.mock import patch, MagicMock

from app.orders.models import Order
from app.products.models import Product
from app.sellers.models import Seller

User = get_user_model()


class OrdersAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.seller = Seller.objects.create(
            user=self.user,
            business_name="Test Seller",
            business_number="1234567890",
        )

        self.product = Product.objects.create(
            name="Sample Product", price=12000, stock=10, seller=self.seller
        )

        self.order = Order.objects.create(
            user=self.user, address="주소", payment_method="card"
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_get_order_list(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

    def test_get_order_detail(self):
        response = self.client.get(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

    def test_update_order_status(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {"status": "shipping", "update_note": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "shipping")

    def test_delete_order(self):
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )


@patch("app.carts.models.CartItem.objects.filter")
@patch("app.orders.services.order_item_service.OrderItemService.create_item")
@patch("app.orders.models.Order.save")
def test_create_order_from_cart_mock(self, mock_order_save, mock_create_item, mock_cart_filter):
    mock_cart_item = MagicMock()
    mock_cart_item.product = self.product
    mock_cart_item.quantity = 2
    mock_cart_filter.return_value.exists.return_value = True
    mock_cart_filter.return_value.__iter__.return_value = [mock_cart_item]

    mock_order_save.return_value = None

    response = self.client.post(
        "/api/orders/",
        {"address": "새 주소", "payment_method": "card"},
        format="json",
    )

    self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    mock_create_item.assert_called_once_with(
        order=self.order,
        product_id=self.product.id,
        quantity=2,
        price_at_purchase=self.product.price
    )