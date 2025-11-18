from django.db import transaction
from django.db.models import F
from app.orders.models import OrderItem
from app.products.models import Product


class OrderItemService:
    @staticmethod
    @transaction.atomic
    def create_item(order, product_id, quantity, price_at_purchase=None):
        try:
            product = Product.objects.select_for_update().get(pk=product_id)
        except Product.DoesNotExist:
            raise ValueError("존재하지 않는 상품입니다.")

        if product.stock < quantity:
            raise ValueError(f"재고 부족: {product.name}")

        product.stock = F("stock") - quantity
        product.save(update_fields=["stock"])
        product.refresh_from_db()  # 재고 최신화

        price_at_purchase = price_at_purchase or product.price

        item = OrderItem.objects.create(
            order=order,
            product_id=product.pk,
            quantity=quantity,
            price_at_purchase=price_at_purchase,
        )

        order.calculate_total()
        order.save(update_fields=["total_amount"])
        return item

    @staticmethod
    @transaction.atomic
    def update_quantity(item, new_quantity):
        if new_quantity <= 0:
            raise ValueError("수량은 1개 이상이어야 합니다.")

        diff = new_quantity - item.quantity
        product = item.product

        if diff > 0 and product.stock < diff:
            raise ValueError(f"재고 부족: {product.name}")

        product.stock = F("stock") - diff
        product.save(update_fields=["stock"])
        product.refresh_from_db()

        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

        item.order.calculate_total()
        item.order.save(update_fields=["total_amount"])
        return item

    @staticmethod
    @transaction.atomic
    def delete_item(item):
        product = item.product
        product.stock = F("stock") + item.quantity
        product.save(update_fields=["stock"])
        product.refresh_from_db()

        order = item.order
        item.delete()

        if not order.items.exists():
            order.delete()
        else:
            order.calculate_total()
            order.save(update_fields=["total_amount"])
        return True
