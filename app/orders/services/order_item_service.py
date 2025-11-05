from app.orders.models import OrderItem
from app.orders.exceptions import OrderNotFound


class OrderItemService:
    @staticmethod
    def get_item(item_id, user=None):
        try:
            if user:
                return OrderItem.objects.get(id=item_id, order__user=user)
            return OrderItem.objects.get(id=item_id)
        except OrderItem.DoesNotExist:
            raise OrderNotFound(f"OrderItem {item_id} not found")

    @staticmethod
    def create_items(order, items_data):
        created_items = []
        for data in items_data:
            item = OrderItem.objects.create(
                order=order,
                product=data["product"],
                quantity=data["quantity"],
                price_at_purchase=data["price_at_purchase"],
            )
            created_items.append(item)
        return created_items

    @staticmethod
    def update_quantity(item_id, quantity, user=None):
        item = OrderItemService.get_item(item_id, user)
        item.quantity = quantity
        item.save()
        return item

    @staticmethod
    def delete_item(item_id, user=None):
        item = OrderItemService.get_item(item_id, user)
        item.delete()
        return True
