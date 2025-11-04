from orders.models import Order, OrderItem
from orders.exceptions import OrderNotFound, InvalidOrderStatus
from products.models import Product


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
    def create_order(user, address, payment_method, items_data):
        order = Order.objects.create(
            user=user, address=address, payment_method=payment_method
        )

        created_items = []
        for item in items_data:
            product = Product.objects.get(id=item["product_id"])
            quantity = item["quantity"]
            price_at_purchase = item.get("price_at_purchase", product.price)

            if product.stock < quantity:
                raise ValueError(f"재고 부족: {product.name}")

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=price_at_purchase,
            )
            created_items.append(order_item)

        order.calculate_total()
        return order

    @staticmethod
    def update_status(order_id, status, user=None):
        order = OrderService.get_order(order_id, user)
        valid_status = [choice[0] for choice in Order.STATUS_CHOICES]
        if status not in valid_status:
            raise InvalidOrderStatus(f"{status} is invalid. Valid: {valid_status}")
        order.status = status
        order.save(update_fields=["status"])
        return order
