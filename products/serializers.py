from rest_framework import serializers

from sellers.models import Seller
from .models import Product, ProductImages, Category, ProductOptionValue


class CategorySerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "group_name", "name"]


class ProductImagesSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(read_only=False)

    class Meta:
        model = ProductImages
        fields = ["image_id", "product", "user", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image_url.url)
        return obj.image_url.url


# 상품 상세 조회 시 옵션과 추가금 표시
class ProductOptionValueSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = ProductOptionValue
        fields = ["id", "category", "extra_price"]


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all()
    )
    images = ProductImagesSerializer(many=True, read_only=True)
    option_values = ProductOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("seller",)


class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["stock", "sold_out"]

    def update(self, instance, validated_data):
        instance.stock = validated_data.get("stock", instance.stock)
        instance.save()
        return instance


class ProductForSellerSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(
        source="seller.user.username", read_only=True
    )
    seller_business_name = serializers.CharField(
        source="seller.business_name", read_only=True
    )
    seller_business_number = serializers.CharField(
        source="seller.business_number", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "product_id",
            "name",
            "origin",
            "price",
            "seller_username",
            "seller_business_name",
            "seller_business_number",
        ]
