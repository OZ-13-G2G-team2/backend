from rest_framework.test import APITestCase
from rest_framework import status

from app.orders.models import Order
from app.orders.services.order_item_service import OrderItemService
from app.products.models import Product, ProductStats
from app.carts.models import Cart, CartItem
from app.address.models import Address
from app.sellers.models import Seller
from app.users.models import User


class OrdersAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.seller = Seller.objects.create(
            user=self.user, business_name="Test Seller", business_number="1234567890"
        )

        self.product = Product.objects.create(
            name="Sample Product", price=12000, stock=10, seller=self.seller
        )
        self.product_stats = ProductStats.objects.create(product=self.product)

        self.address = Address.objects.create(
            user=self.user,
            recipient_name="홍길동",
            phone_number="010-1234-5678",
            postal_code="12345",
            street_address="테스트로 1길 1",
        )

        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.order = Order.objects.create(
            user=self.user,
            address=self.address,
            payment_method="card",
            total_amount=self.product.price * 2,
            status="pending",
        )
        OrderItemService.create_item(
            order=self.order,
            product_id=self.product.pk,
            quantity=2,
            price_at_purchase=self.product.price,
        )

    def test_get_order_list(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
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

    def test_update_order_status_invalid_status(self):
        response = self.client.patch(
            f"/api/orders/{self.order.pk}/status/",
            {"status": "invalid_status"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_now_creates_order_and_order_item(self):
        product = Product.objects.create(
            name="BuyNow Product", price=12000, stock=10, seller=self.seller
        )

        response = self.client.post(
            "/api/orders/buy-now/",
            {
                "product_id": product.pk,
                "quantity": 1,
                "address_id": self.address.pk,
                "payment_method": "card",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.items.count(), 1)

        product.refresh_from_db()
        self.assertEqual(product.stock, 9)

    def test_buy_now_insufficient_stock(self):
        product = Product.objects.create(
            name="LowStock Product", price=12000, stock=0, seller=self.seller
        )
        response = self.client.post(
            "/api/orders/buy-now/",
            {
                "product_id": product.pk,
                "quantity": 1,
                "address_id": self.address.pk,
                "payment_method": "card",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_purchase_empty_cart(self):
        CartItem.objects.filter(cart__user=self.user).delete()
        _data = {
            "address_id": self.address.id,
            "payment_method": "card",
        }

        response = self.client.post(
            "/api/orders/cart-purchase/",
            {"address_id": self.address.pk, "payment_method": "card"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "장바구니에 상품이 없습니다.")

    def test_cart_purchase_creates_order_and_clears_cart(self):
        CartItem.objects.filter(cart=self.cart).delete()
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        _data = {
            "address_id": self.address.id,
            "payment_method": "card",
        }

        response = self.client.post(
            "/api/orders/cart-purchase/",
            {"address_id": self.address.pk, "payment_method": "card"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())

    def test_order_list_filter_by_user(self):
        response = self.client.get("/api/orders/")
        for order in response.data:
            self.assertEqual(order["user"], self.user.id)
