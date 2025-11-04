from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()


class OrdersAPITest(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )

        # 제품 생성 시 seller 필드는 신경 쓰지 않음
        self.product = Product.objects.create(name="Test Product", price=100, stock=10)

        self.order = Order.objects.create(user=self.user, total_amount=0)

        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price_at_purchase=100
        )

        # 주문 총액 계산
        self.order.calculate_total()
        self.order.save()

    def test_get_order_list(self):
        response = self.client.get("/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["orders"]), 1)
        self.assertEqual(response.data["orders"][0]["order_id"], self.order.id)

    def test_get_order_detail(self):
        response = self.client.get(f"/orders/{self.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_id"], self.order.id)

    def test_update_order_status(self):
        response = self.client.patch(
            f"/orders/{self.order.id}/status/",
            {"status": "shipping", "update_note": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "shipping")

    def test_delete_order(self):
        response = self.client.delete(f"/orders/{self.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "canceled")
