from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

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
