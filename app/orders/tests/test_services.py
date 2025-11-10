from django.test import TestCase
from django.contrib.auth import get_user_model


from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.orders.services import OrderService, OrderItemService
from app.sellers.models import Seller

User = get_user_model()


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

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

        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=12000
        )

    def test_update_order_status(self):
        updated_order = OrderService.update_status(
            self.order.id, "shipping", user=self.user
        )
        self.assertEqual(updated_order.status, "shipping")


class OrderItemServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

        self.seller = Seller.objects.create(
            user=self.user, business_name="Test Seller", business_number="1234567890"
        )

        self.product = Product.objects.create(
            name="Sample Product", price=12000, stock=10, seller=self.seller
        )

        self.order = Order.objects.create(
            user=self.user, address="주소", payment_method="card"
        )

        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=12000
        )

    def test_update_quantity(self):
        updated_item = OrderItemService.update_quantity(self.order_item, 3)
        self.assertEqual(updated_item.quantity, 3)
