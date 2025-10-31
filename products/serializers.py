from rest_framework import serializers
from .models import Product, ProductImages, Category, ProductOptionValue, ProductOptions


class ProductOptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionValue
        fields = ['value', 'extra_price']

class ProductOptionSerializer(serializers.ModelSerializer):
    values = ProductOptionValueSerializer(many=True, read_only=True)
    class Meta:
        model = ProductOptions
        fields = ['name', 'values']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'group']

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image_url']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=True)
    images = ProductImagesSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'seller_id', 'categories', 'price',
                  'overseas_shipping', 'delivery_fee', 'description',
                  'sold_out', 'images', 'options']
