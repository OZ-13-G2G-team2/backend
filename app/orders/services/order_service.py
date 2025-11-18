from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from app.orders.models import Order
from app.carts.models import CartItem
from app.orders.services.order_item_service import OrderItemService
from app.orders.exceptions import OrderNotFound, InvalidOrderStatus
from app.products.models import ProductStats


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, serializer):

        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items.exists():
            raise ValidationError("장바구니에 상품이 없습니다.")

        order = serializer.save()

        for cart_item in cart_items:
            OrderItemService.create_item(
                order=order,
                product_id=cart_item.product.pk,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price,
            )

        cart_items.delete()
        order.calculate_total()
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def update_status(order_id, new_status, user):

        try:
            order = Order.objects.select_for_update().get(id=order_id, user=user)
        except Order.DoesNotExist:
            raise OrderNotFound()

        valid_status = ["pending", "completed", "cancelled", "shipping", "delivered"]
        if new_status not in valid_status:
            raise InvalidOrderStatus()

        previous_status = order.status
        order.status = new_status
        order.save()

        if previous_status != "completed" and new_status == "completed":
            for item in order.items.all():
                stats, _ = ProductStats.objects.get_or_create(product=item.product)
                stats.sales_count = F("sales_count") + item.quantity
                stats.save()
                stats.refresh_from_db()

        return order
