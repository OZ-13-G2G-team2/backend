from rest_framework import serializers
from .models import Product, ProductImages, Category, ProductOptionValue


class CategorySerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'group_name', 'name']

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image_id','image_url']

# 상품 상세 조회 시 옵션과 추가금 표시
class ProductOptionValueSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = ProductOptionValue
        fields = ['id', 'category', 'extra_price']

class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    images = ProductImagesSerializer(many=True, read_only=True)
    option_values = ProductOptionValueSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("seller",)


