from rest_framework import serializers
from app.orders.models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        help_text="주문 수량 (1 이상)",
    )
    price_at_purchase = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        help_text="상품 구매 당시 가격 (음수 불가)",
    )
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "quantity",
            "price_at_purchase",
            "subtotal",
        ]
