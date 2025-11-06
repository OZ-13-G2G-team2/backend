from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from app.orders.models import Order

User = get_user_model()


class OrdersAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.order = Order.objects.create(
            user=self.user, address="m", payment_method="card"
        )

    def test_get_order_list(self):
        response = self.client.get("/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 리스트로 응답하는 형태에 맞게 수정
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["order_id"], self.order.id)

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
        # 삭제 응답 방식이 200/204 둘 중 하나일 경우 허용
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )
