from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from app.sellers.models import Seller

User = get_user_model()


class UserAuthTests(APITestCase):

    def setUp(self):
        # 활성화된 일반 유저
        self.active_user = User.objects.create_user(
            email="active@example.com",
            username="active_user",
            password="StrongPassword123!",
            is_active=True,
        )

        # 비활성 유저
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive_user",
            password="StrongPassword123!",
            is_active=False,
        )

        # 셀러 유저
        self.seller_user = User.objects.create_user(
            email="seller@example.com",
            username="seller_user",
            password="StrongPassword123!",
            is_active=True,
        )
        Seller.objects.create(
            user=self.seller_user,
            business_name="Test Biz",
            business_address="Test Address",
            business_number="1234567890",
        )

    # ----------------------
    # 로그인 테스트
    # ----------------------

    def test_login_active_user_success(self):
        url = reverse("user_auth:login")
        data = {"email": "active@example.com", "password": "StrongPassword123!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_inactive_user_error(self):
        url = reverse("user_auth:login")
        data = {"email": "inactive@example.com", "password": "StrongPassword123!"}
        response = self.client.post(url, data)

        # 비활성화 유저는 400 반환
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("detail"), "이메일 또는 비밀번호가 올바르지 않습니다.")

    def test_login_seller_user_token_contains_is_seller(self):
        url = reverse("user_auth:login")
        data = {"email": "seller@example.com", "password": "StrongPassword123!"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Signing key 올바르게 가져오기
        signing_key = settings.SIMPLE_JWT.get("SIGNING_KEY", settings.SECRET_KEY)
        token_backend = TokenBackend(
            algorithm="HS256",
            signing_key=signing_key
        )

        decoded = token_backend.decode(response.data["access"], verify=False)
        self.assertTrue(decoded.get("is_seller", False))
    # ----------------------
    # 로그아웃 테스트
    # ----------------------
    def test_logout_success(self):
        # 로그인 후 refresh 토큰 발급
        url = reverse("user_auth:login")
        data = {"email": "active@example.com", "password": "StrongPassword123!"}
        response = self.client.post(url, data)
        refresh_token = response.data["refresh"]

        logout_url = reverse("user_auth:logout")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        resp = self.client.post(logout_url, {"refresh": refresh_token}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(resp.data.get("detail"), "로그아웃 되었습니다.")

    def test_logout_invalid_token_error(self):
        logout_url = reverse("user_auth:logout")
        self.client.force_authenticate(user=self.active_user)

        resp = self.client.post(logout_url, {"refresh": "invalidtoken"}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("detail"), "유효하지 않은 토큰입니다.")

    # ----------------------
    # 토큰 갱신 테스트
    # ----------------------
    def test_token_refresh_success(self):
        url = reverse("user_auth:login")
        data = {"email": "active@example.com", "password": "StrongPassword123!"}
        response = self.client.post(url, data)
        refresh_token = response.data["refresh"]

        refresh_url = reverse("user_auth:token-refresh")
        resp = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_token_refresh_invalid_error(self):
        refresh_url = reverse("user_auth:token-refresh")
        resp = self.client.post(refresh_url, {"refresh": "invalidtoken"}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
