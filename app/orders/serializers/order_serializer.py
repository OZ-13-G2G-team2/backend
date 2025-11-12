from rest_framework import serializers
from app.orders.models import Order
from app.orders.serializers.order_item_serializer import OrderItemSerializer


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_name",
            "order_date",
            "address",
            "total_amount",
            "status",
            "payment_method",
            "created_at",
            "updated_at",
            "items",

        ]
