from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Product
from django.contrib.auth.models import User as AuthUser

User = get_user_model()


class OrderItemAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

        self.seller = AuthUser.objects.create_user(
            username="seller", password="sellerpass"
        )
        self.product = Product.objects.create(
            name="Test Product", price=100, stock=10, seller=self.seller
        )

        self.order = Order.objects.create(
            user=self.user, user_address="test address", payment_method="card"
        )

        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=100
        )

    def test_get_order_items(self):
        response = self.client.get(f"/order-items/?order_id={self.order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_order_item_quantity(self):
        response = self.client.patch(
            f"/order-items/{self.order_item.id}/",
            {"quantity": 3, "change_reason": "테스트"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_quantity"], 3)

    def test_delete_order_item(self):
        response = self.client.delete(f"/order-items/{self.order_item.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
