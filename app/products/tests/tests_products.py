# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.urls import reverse
# from app.sellers.models import Seller
# from app.products.models import Product, Category, CategoryGroup
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
#
# class ProductAPITestCase(TestCase):
#     def setUp(self):
#         # 사용자/판매자 생성
#         self.user = User.objects.create_user(email="seller@test.com", password="testpass123")
#         self.seller = Seller.objects.create(user=self.user, business_name="테스트상점")
#
#         self.other_user = User.objects.create_user(email="other@test.com", password="testpass123")
#
#         # 카테고리/그룹 생성
#         self.group = CategoryGroup.objects.create(name="테스트그룹")
#         self.category = Category.objects.create(name="테스트카테고리", group=self.group)
#
#         # 상품 생성
#         self.product = Product.objects.create(
#             seller=self.seller,
#             name="테스트상품",
#             origin="한국",
#             price=10000,
#             sold_out=False
#         )
#         self.product.categories.add(self.category)
#
#         self.client = APIClient()
#
#     # 상품 목록 조회
#     def test_product_list(self):
#         url = reverse("product-list")  # urls.py에서 name 설정 필요
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(len(response.data) >= 1)
#
#     # 상품 등록
#     def test_product_create_authenticated(self):
#         self.client.force_authenticate(user=self.user)
#         url = reverse("product-create")
#         data = {
#             "name": "신규상품",
#             "origin": "한국",
#             "price": 15000,
#             "categories": [self.category.id],
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data["name"], "신규상품")
#
#     def test_product_create_unauthenticated(self):
#         url = reverse("product-create")
#         data = {"name": "신규상품", "origin": "한국", "price": 15000}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 403)
#
#
#     # 상품 수정
#     def test_product_update_by_owner(self):
#         self.client.force_authenticate(user=self.user)
#         url = reverse("product-detail", args=[self.product.product_id])
#         data = {"price": 20000}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["price"], 20000)
#
#     def test_product_update_by_other(self):
#         self.client.force_authenticate(user=self.other_user)
#         url = reverse("product-detail", args=[self.product.product_id])
#         data = {"price": 20000}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, 403)
#
#
#     # 판매자별 상품 목록
#
#     def test_seller_products(self):
#         url = reverse("seller-products", args=[self.user.id])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(all(p["sold_out"] is False for p in response.data))
#
#     def test_seller_products_not_exist(self):
#         url = reverse("seller-products", args=[9999])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#
#     # 카테고리별 조회
#     def test_products_by_category(self):
#         url = reverse("products-by-category", args=[self.category.id])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(all(p["sold_out"] is False for p in response.data))
