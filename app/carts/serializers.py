from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    thumbnail = serializers.CharField(source="product.thumbnail", read_only=True)
    price = serializers.IntegerField(source="product.price", read_only=True)
    original_price = serializers.IntegerField(
        source="product.original_price", read_only=True
    )
    delivery_fee = serializers.IntegerField(
        source="product.delivery_fee", read_only=True
    )

    # 계산 필드
    sub_total = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
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
        # 상품 가격 * 수량
        return obj.product.price * obj.quantity

    def get_discount_amount(self, obj):
        # 할인금액 = (정가 - 판매가) * 수량
        return (obj.product.original_price - obj.product.price) * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    # 장바구니 전체 가격
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
        # 모든 상품 가격 합 (할인 반영된 판매가격 기준)
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_total_delivery_fee(self, obj):
        # 모든 상품의 배송비 합
        return sum(item.product.delivery_fee for item in obj.items.all())

    def get_final_price(self, obj):
        # 최종 결제 금액 (상품 총액 + 배송비)
        return self.get_total_product_price(obj) + self.get_total_delivery_fee(obj)
