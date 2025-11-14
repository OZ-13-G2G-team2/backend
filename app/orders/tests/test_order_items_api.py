from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from app.address.models import Address
from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.sellers.models import Seller
import uuid

User = get_user_model()


def unique_email(base="user"):
    return f"{base}_{uuid.uuid4().hex[:6]}@example.com"


class OrderItemsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser_orderitemsapi",
            email=unique_email("orderitemsapi"),
            password="testpass",
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

        self.address = Address.objects.create(
            user=self.user,
            recipient_name="홍길동",
            phone_number="010-1234-5678",
            postal_code="12345",
            street_address="테스트로 1길 1",
        )

        self.order = Order.objects.create(
            user=self.user, address=self.address, payment_method="card"
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
