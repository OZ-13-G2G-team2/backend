from django.db.models import F
from rest_framework.test import APITestCase
from rest_framework import status

from app.orders.models import Order, OrderItem
from app.orders.services.order_item_service import OrderItemService
from app.products.models import Product, ProductStats
from app.carts.models import Cart, CartItem
from app.address.models import Address
from app.sellers.models import Seller
from app.users.models import User


class OrdersAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass"
        )
        self.client.force_authenticate(user=self.user)


        self.seller = Seller.objects.create(
            user=self.user,
            business_name="Test Seller",
            business_number="1234567890",
        )


        self.product = Product.objects.create(
            name="Sample Product",
            price=12000,
            stock=10,
            seller=self.seller
        )
        self.product_stats = ProductStats.objects.create(product=self.product)


        self.address = Address.objects.create(
            user=self.user,
            recipient_name="홍길동",
            phone_number="010-1234-5678",
            postal_code="12345",
            street_address="테스트로 1길 1"
        )


        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)


        self.order = Order.objects.create(
            user=self.user,
            address=self.address,
            payment_method="card",
            total_amount=self.product.price * 2,
            status="pending"
        )

        OrderItemService.create_item(
            order=self.order,
            product_id=self.product.pk,
            quantity=2,
            price_at_purchase=self.product.price
        )

    def test_get_order_list(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.pk)

    def test_get_order_detail(self):
        response = self.client.get(f"/api/orders/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.pk)

    def test_update_order_status(self):
        response = self.client.patch(
            f"/api/orders/{self.order.pk}/status/",
            {"status": "shipping", "update_note": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "shipping")

    def test_update_order_status_completed_increases_sales_count(self):
        response = self.client.patch(
            f"/api/orders/{self.order.pk}/status/",
            {"status": "completed", "update_note": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.product_stats.refresh_from_db()
        self.assertEqual(self.product_stats.sales_count, 2)
