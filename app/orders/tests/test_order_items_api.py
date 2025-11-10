from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.sellers.models import Seller

User = get_user_model()


class OrderItemsAPITest(APITestCase):
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
            name="티셔츠", price=12000, stock=10, seller=self.seller
        )

        self.order = Order.objects.create(
            user=self.user, address="주소", payment_method="card"
        )

        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=12000
        )

    def test_get_order_items(self):
        response = self.client.get(
            f"/api/orders/items/by_order/?order_id={self.order.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_order_item_quantity(self):
        response = self.client.patch(
            f"/api/orders/items/{self.order_item.id}/",
            {"quantity": 3, "change_reason": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 3)

    def test_delete_order_item(self):
        response = self.client.delete(f"/api/orders/items/{self.order_item.id}/")
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )
