from django.db import models
from app.orders.models import Order
from app.products.models import Product
from django.utils import timezone


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="주문"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="상품",
    )
    change_reason = models.CharField("변경 사유", max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(verbose_name="수량")
    price_at_purchase = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="구매 당시 가격"
    )

    class Meta:
        db_table = "order_items"
        verbose_name = "주문 상세"
        verbose_name_plural = "주문 상세 목록"
        ordering = ["order"]

    def __str__(self):
        return f"{self.order.id}번 주문 - {self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def total_with_tax(self, tax_rate=0.1):
        return self.subtotal * (1 + tax_rate)
