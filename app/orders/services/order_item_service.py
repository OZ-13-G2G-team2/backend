from django.db import transaction
from app.orders.models import OrderItem
from app.products.models import Product
from django.db.models import F


class OrderItemService:
    @staticmethod
    @transaction.atomic
    def create_item(order, product_id, quantity, price_at_purchase=None):
        product = Product.objects.select_for_update().get(id=product_id)

        if product.stock < quantity:
            raise ValueError(f"재고 부족: {product.name}")

        product.stock = F("stock") - quantity
        product.save(update_fields=["stock"])

        price_at_purchase = price_at_purchase or product.price

        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=price_at_purchase,
        )

        order.calculate_total()
        return item

    @staticmethod
    @transaction.atomic
    def update_quantity(item, new_quantity):
        diff = new_quantity - item.quantity
        product = item.product

        if diff > 0 and product.stock < diff:
            raise ValueError(f"재고 부족: {product.name}")

        product.stock = F("stock") - diff
        product.save(update_fields=["stock"])

        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

        item.order.calculate_total()
        return item

    @staticmethod
    @transaction.atomic
    def delete_item(item):
        product = item.product
        product.stock = F("stock") + item.quantity
        product.save(update_fields=["stock"])

        order = item.order
        item.delete()
        order.calculate_total()
