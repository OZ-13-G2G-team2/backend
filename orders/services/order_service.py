from orders.models import Order
from orders.exceptions import OrderNotFound, InvalidOrderStatus


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
    def update_status(order_id, status, user=None):
        order = OrderService.get_order(order_id, user)
        valid_status = [choice[0] for choice in Order.STATUS_CHOICES]
        if status not in valid_status:
            raise InvalidOrderStatus(f"{status} is invalid. Valid: {valid_status}")
        order.status = status
        order.save()
        return order

    @staticmethod
    def delete_order(order_id, user=None):
        order = OrderService.get_order(order_id, user)
        order.delete()
        return True
