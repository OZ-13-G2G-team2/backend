from rest_framework import serializers

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
    thumbnail = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source="seller.user.username", read_only=True)
    seller_business_name = serializers.CharField(source="seller.business_name", read_only=True)
    seller_business_address = serializers.CharField(source="seller.business_address", read_only=True)
    seller_business_number = serializers.CharField(source="seller.business_number", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id", "name", "price", "thumbnail",
            "seller_name", "seller_name", "seller_business_name",
            "seller_business_address", "seller_business_number","created_at"
        ]
        read_only_fields = ("seller",)

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if not first_image:
            return None
        return self.context['request'].build_absolute_uri(first_image.image_url)


class ProductCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )
    seller_username = serializers.CharField(
        source="seller.user.username", read_only=True
    )
    seller_business_name = serializers.CharField(
        source="seller.business_name", read_only=True
    )
    seller_business_number = serializers.CharField(
        source="seller.business_number", read_only=True
    )
    seller_business_address = serializers.CharField(
        source="seller.business_address", read_only=True
    )
    images = ProductImagesSerializer(many=True, write_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id", "seller", "name", "origin", "stock", "price",
            "overseas_shipping", "delivery_fee", "description", "sold_out",
            "created_at", "updated_at", "categories", "images", "seller_username",
            "seller_business_name", "seller_business_number", "seller_business_address",
        ]
        read_only_fields = ("seller",)


    def create(self, validated_data):
        images_data = validated_data.pop("images", [])  # 이미지 데이터 분리
        categories_data = validated_data.pop("categories", []) # 카테고리 분리
        product = Product.objects.create(**validated_data)

        product.categories.set(categories_data)

        request_user = self.context['request'].user
        validated_data["seller"] = request_user

        for image_data in images_data:
            ProductImages.objects.create(
                product=product,
                user=request_user,
                **image_data
            )
        return product

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
    seller_business_address = serializers.CharField(
        source="seller.business_address", read_only=True
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
            "seller_business_address",
            "seller_business_number",
        ]

class ProductDetailWithSellerSerializer(ProductSerializer):
    categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    images = ProductImagesSerializer(
        many=True,
        read_only=True,
    )
    option_values = ProductOptionValueSerializer(many=True, read_only=True)

    seller_username = serializers.CharField(
        source="seller.user.username", read_only=True
    )
    seller_business_name = serializers.CharField(
        source="seller.business_name", read_only=True
    )
    seller_business_address = serializers.CharField(
        source="seller.business_address", read_only=True
    )
    seller_business_number = serializers.CharField(
        source="seller.business_number", read_only=True
    )
    class Meta:
        model = Product
        fields = [
            "product_id", "seller", "name", "origin", "stock", "price",
            "overseas_shipping", "delivery_fee", "description", "sold_out",
            "created_at", "updated_at", "categories", "images", "option_values",
            "seller_username", "seller_business_name", "seller_business_address",
            "seller_business_number",
        ]
        read_only_fields = ("seller",)