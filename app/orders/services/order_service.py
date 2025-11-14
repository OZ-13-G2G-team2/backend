from django.db import transaction
from app.orders.models import Order
from app.orders.exceptions import OrderNotFound, InvalidOrderStatus
from app.carts.models import CartItem
from app.orders.services.order_item_service import OrderItemService
from app.products.models import Product


class OrderService:
    @staticmethod
    def get_order(order_id, user=None):
        try:
            if user:
                return Order.objects.get(id=order_id, user=user)
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise OrderNotFound(f"Order {order_id} not found")

    @staticmethod
    def update_status(order_id, new_status, user=None):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise OrderNotFound()

        if new_status not in ["pending", "shipping", "completed", "cancelled","delivered"]:
            raise InvalidOrderStatus()

        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        return order

    @staticmethod
    def delete_order(order_id, user=None):
        order = OrderService.get_order(order_id, user)
        order.delete()
        return True

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, serializer):
        order = serializer.save(user=user)
        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items.exists():
            raise ValueError("장바구니가 비어 있습니다.")

        for item in cart_items:
            OrderItemService.create_item(
                order=order,
                product_id=item.product.id,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )

        cart_items.delete()
        order.calculate_total()
        return order

    @staticmethod
    @transaction.atomic
    def create_order_buy_now(user, product_id, quantity, address, payment_method):
        try:
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError("존재하지 않는 상품입니다.")

        if product.stock < quantity:
            raise ValueError("재고가 부족합니다.")

        order = Order.objects.create(
            user=user,
            address=address,
            payment_method=payment_method,
            total_amount=product.price * quantity,
            status="pending",
        )

        OrderItemService.create_item(
            order=order,
            product_id=product.id,
            quantity=quantity,
            price_at_purchase=product.price,
        )

        order.calculate_total()
        return order
