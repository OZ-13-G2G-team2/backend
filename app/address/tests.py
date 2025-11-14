from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from .models import Address

User = get_user_model()


class AddressAPITestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.address = Address.objects.create(
            user=self.user,
            recipient_name="홍길동",
            phone_number="010-1234-5678",
            postal_code="12345",
            country="대한민국",
            state="서울",
            city="강남구",
            street_address="테헤란로 123",
            detail_address="101호",
            is_default=True,
        )

    def test_list_addresses(self):
        url = reverse("address:address-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_address(self):
        url = reverse("address:address-detail", args=[self.address.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recipient_name"], self.address.recipient_name)

    def test_create_address(self):
        url = reverse("address:address-list")
        data = {
            "recipient_name": "김철수",
            "phone_number": "010-9876-5432",
            "postal_code": "54321",
            "country": "대한민국",
            "state": "부산",
            "city": "해운대구",
            "street_address": "센텀로 456",
            "detail_address": "202호",
            "is_default": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["recipient_name"], "김철수")

    def test_update_address(self):
        url = reverse("address:address-detail", args=[self.address.id])
        data = {
            "recipient_name": "홍길동 수정",
            "phone_number": self.address.phone_number,
            "postal_code": self.address.postal_code,
            "country": self.address.country,
            "state": self.address.state,
            "city": self.address.city,
            "street_address": self.address.street_address,
            "detail_address": self.address.detail_address,
            "is_default": self.address.is_default,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recipient_name"], "홍길동 수정")

    def test_delete_address(self):
        url = reverse("address:address-detail", args=[self.address.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Address.objects.filter(id=self.address.id).exists())
