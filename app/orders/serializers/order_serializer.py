from rest_framework import serializers
from app.orders.models import Order
from app.orders.serializers.order_item_serializer import OrderItemSerializer
from app.address.models import Address
from rest_framework.exceptions import ValidationError


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


class CartPurchaseOrderSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(write_only=True)
    address = serializers.PrimaryKeyRelatedField(read_only=True)
    payment_method = serializers.CharField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "address_id",
            "payment_method",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        address_id = attrs.get("address_id")

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise ValidationError({"address_id": "존재하지 않는 주소입니다."})

        attrs["address"] = address
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        validated_data.pop("address_id", None)

        if "status" not in validated_data:
            validated_data["status"] = "pending"

        payment_method = validated_data.pop("payment_method", None)
        validated_data["payment_method"] = payment_method

        return super().create(validated_data)
