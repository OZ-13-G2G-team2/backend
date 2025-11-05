from rest_framework import serializers
from app.orders.models import Order, OrderItem
from app.orders.serializers.order_item_serializer import OrderItemSerializer
from app.products.models import Product


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=False)
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

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product_id = (
                item_data["product"].id
                if hasattr(item_data["product"], "id")
                else item_data["product"]
            )
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data["quantity"],
                price_at_purchase=item_data.get("price_at_purchase") or product.price,
            )
        order.calculate_total()
        return order
