from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)

    product_name = serializers.CharField(source="product.name", read_only=True)
    thumbnail = serializers.CharField(source="product.thumbnail", read_only=True)
    price = serializers.IntegerField(source="product.price", read_only=True)
    original_price = serializers.IntegerField(
        source="product.original_price", read_only=True
    )
    delivery_fee = serializers.IntegerField(
        source="product.delivery_fee", read_only=True
    )

    sub_total = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "product_name",
            "thumbnail",
            "price",
            "original_price",
            "delivery_fee",
            "quantity",
            "sub_total",
            "discount_amount",
        ]

    def get_sub_total(self, obj):
        return obj.product.price * obj.quantity

    def get_discount_amount(self, obj):
        original = getattr(obj.product, "original_price", obj.product.price)
        return (original - obj.product.price) * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    total_product_price = serializers.SerializerMethodField()
    total_delivery_fee = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "total_product_price",
            "total_delivery_fee",
            "final_price",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]

    def get_total_product_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_total_delivery_fee(self, obj):
        return sum(item.product.delivery_fee for item in obj.items.all())

    def get_final_price(self, obj):
        return self.get_total_product_price(obj) + self.get_total_delivery_fee(obj)
