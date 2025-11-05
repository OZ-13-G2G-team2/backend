from django.test import TestCase
from django.contrib.auth import get_user_model
from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.orders.services import OrderService, OrderItemService

User = get_user_model()


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.product = Product.objects.create(name="m", price=12000)
        self.order = Order.objects.create(
            user=self.user, user_address="m", payment_method="card"
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
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.product = Product.objects.create(name="m", price=12000)
        self.order = Order.objects.create(
            user=self.user, user_address="m", payment_method="card"
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=12000
        )

    def test_update_quantity(self):
        updated_item = OrderItemService.update_quantity(
            self.order_item.id, 3, user=self.user
        )
        self.assertEqual(updated_item.quantity, 3)
