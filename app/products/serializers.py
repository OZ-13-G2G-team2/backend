from rest_framework import serializers

from .models import Product, ProductImages, Category, ProductOptionValue, ProductStats
from drf_spectacular.utils import extend_schema_field
import json
from ..sellers.models import Seller


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
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_input = serializers.CharField(write_only=True)
    extra_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ProductOptionValue
        fields = ["category_name", "category_input", "extra_price"]

    def create(self, validated_data):
        category_name = validated_data.pop("category_input")
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"존재하지 않는 카테고리: {category_name}"
            )
        return ProductOptionValue.objects.create(category=category, **validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop("category_input", None)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                raise serializers.ValidationError(
                    f"존재하지 않는 카테고리: {category_name}"
                )
            instance.category = category

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance


# 상품 통계
class ProductStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStats
        fields = ["sales_count", "review_count", "wish_count"]


class ProductSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
    seller_name = serializers.CharField(source="seller.user.username", read_only=True)
    seller_business_name = serializers.CharField(
        source="seller.business_name", read_only=True
    )
    seller_business_address = serializers.CharField(
        source="seller.business_address", read_only=True
    )
    seller_business_number = serializers.CharField(
        source="seller.business_number", read_only=True
    )
    discount_rate = serializers.SerializerMethodField()
    categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    review_count = serializers.SerializerMethodField()
    sales_count = serializers.SerializerMethodField()
    wish_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "product_id",
            "seller_id",
            "name",
            "categories",
            "origin",
            "price",
            "discount_price",
            "discount_rate",
            "thumbnail",
            "review_count",
            "sales_count",
            "wish_count",
            "seller_name",
            "seller_business_name",
            "seller_business_address",
            "seller_business_number",
            "sold_out",
            "created_at",
        ]
        read_only_fields = ("seller",)

    def get_discount_rate(self, obj):
        if obj.price and obj.discount_price and obj.discount_price < obj.price:
            return round(
                (float(obj.price) - float(obj.discount_price)) / float(obj.price) * 100,
                2,
            )
        return 0

    def get_review_count(self, obj):
        return getattr(obj.stats, "review_count", 0) if hasattr(obj, "stats") else 0

    def get_sales_count(self, obj):
        return getattr(obj.stats, "sales_count", 0) if hasattr(obj, "stats") else 0

    def get_wish_count(self, obj):
        return getattr(obj.stats, "wish_count", 0) if hasattr(obj, "stats") else 0

    @extend_schema_field(serializers.CharField())
    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if not first_image:
            return None
        return self.context["request"].build_absolute_uri(first_image.image_url)


class ProductCreateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    option_values = ProductOptionValueSerializer(many=True, required=False)
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
    images = ProductImagesSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "seller_id",
            "name",
            "origin",
            "stock",
            "price",
            "discount_price",
            "overseas_shipping",
            "delivery_fee",
            "description",
            "sold_out",
            "created_at",
            "updated_at",
            "images",
            "categories",
            "option_values",
            "seller_username",
            "seller_business_name",
            "seller_business_number",
            "seller_business_address",
        ]
        read_only_fields = ("seller",)

    def create(self, validated_data):
        request = self.context.get("request")

        raw_option = request.data.get("option_values")
        images_data = (
            request.FILES.getlist("images", []) if request.FILES else []
        )  # 이미지 데이터 분리
        categories_data = validated_data.pop("categories", [])

        seller = validated_data.pop("seller")
        if seller is None or not Seller.objects.filter(id=seller.id).exists():
            raise serializers.ValidationError("판매자 계정이 존재하지 않습니다.")

        product = Product.objects.create(seller=seller, **validated_data)

        if categories_data:
            product.categories.set(categories_data)

        for image_data in images_data:
            ProductImages.objects.create(
                product=product, user=seller.user, image_url=image_data
            )

        if raw_option:
            try:
                option_data = json.loads(raw_option)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "option_values 필드는 JSON 배열 JSON 형식이어야 합니다."
                )
        else:
            option_data = None

        if option_data is not None:
            for option in option_data:
                category_name = option.get("category_input")
                extra_price = option.get("extra_price", 0)

                category = Category.objects.filter(name=category_name).first()
                if not category:
                    raise serializers.ValidationError(
                        f"옵션 카테고리 {category_name} 이(가) 존재하지 않습니다."
                    )

                ProductOptionValue.objects.create(
                    product=product, category=category, extra_price=extra_price
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
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
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
    discount_rate = serializers.SerializerMethodField()

    sales_count = serializers.IntegerField(source="stats.sales_count", read_only=True)
    review_count = serializers.IntegerField(source="stats.review_count", read_only=True)
    wish_count = serializers.IntegerField(source="stats.wish_count", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "seller_id",
            "name",
            "origin",
            "price",
            "discount_price",
            "discount_rate",
            "review_count",
            "sales_count",
            "wish_count",
            "seller_username",
            "seller_business_name",
            "seller_business_address",
            "seller_business_number",
        ]

    def get_discount_rate(self, obj):
        if obj.price and obj.discount_price and obj.discount_price < obj.price:
            return round(
                (float(obj.price) - float(obj.discount_price)) / float(obj.price) * 100,
                2,
            )
        return 0

    def get_review_count(self, obj):
        return getattr(obj.stats, "review_count", 0) if hasattr(obj, "stats") else 0

    def get_sales_count(self, obj):
        return getattr(obj.stats, "sales_count", 0) if hasattr(obj, "stats") else 0

    def get_wish_count(self, obj):
        return getattr(obj.stats, "wish_count", 0) if hasattr(obj, "stats") else 0


class ProductDetailWithSellerSerializer(ProductSerializer):
    categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    images = ProductImagesSerializer(many=True, read_only=True, required=False)
    option_values = ProductOptionValueSerializer(many=True, read_only=True)

    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
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
    discount_rate = serializers.SerializerMethodField()

    sales_count = serializers.IntegerField(source="stats.sales_count", read_only=True)
    review_count = serializers.IntegerField(source="stats.review_count", read_only=True)
    wish_count = serializers.IntegerField(source="stats.wish_count", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "seller_id",
            "name",
            "origin",
            "stock",
            "price",
            "discount_price",
            "discount_rate",
            "review_count",
            "sales_count",
            "wish_count",
            "overseas_shipping",
            "delivery_fee",
            "description",
            "sold_out",
            "created_at",
            "updated_at",
            "categories",
            "option_values",
            "images",
            "seller_username",
            "seller_business_name",
            "seller_business_address",
            "seller_business_number",
        ]
        read_only_fields = ("seller",)

    def get_discount_rate(self, obj):
        if obj.price and obj.discount_price and obj.discount_price < obj.price:
            return round(
                (float(obj.price) - float(obj.discount_price)) / float(obj.price) * 100,
                2,
            )
        return 0

    def get_review_count(self, obj):
        return getattr(obj.stats, "review_count", 0) if hasattr(obj, "stats") else 0

    def get_sales_count(self, obj):
        return getattr(obj.stats, "sales_count", 0) if hasattr(obj, "stats") else 0

    def get_wish_count(self, obj):
        return getattr(obj.stats, "wish_count", 0) if hasattr(obj, "stats") else 0


class ProductUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    option_values = ProductOptionValueSerializer(many=True, required=False)

    discount_rate = serializers.SerializerMethodField()

    images = ProductImagesSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            "name",
            "origin",
            "stock",
            "price",
            "discount_price",
            "discount_rate",
            "overseas_shipping",
            "delivery_fee",
            "description",
            "sold_out",
            "categories",
            "option_values",
            "images",
        ]

    def get_discount_rate(self, obj):
        if obj.price and obj.discount_price and obj.discount_price < obj.price:
            return round(
                (float(obj.price) - float(obj.discount_price)) / float(obj.price) * 100,
                2,
            )
        return 0

    def update(self, instance, validated_data):
        request = self.context.get("request")

        categories_data = validated_data.pop("categories", None)
        if categories_data is not None:
            # 기존 카테고리 유지 + 새로운 것 추가 (중복 제거)
            existing_ids = set(instance.categories.values_list("id", flat=True))
            valid_ids = set(
                Category.objects.filter(id__in=categories_data).values_list(
                    "id", flat=True
                )
            )
            all_ids = list(existing_ids | valid_ids)  # 합집합
            instance.categories.set(all_ids)

        # 일반 필드
        for attr, value in validated_data.items():
            if attr not in ["option_values", "images"]:
                setattr(instance, attr, value)
        instance.save()

        raw_option = request.data.get("option_values")

        if raw_option:
            try:
                option_data = json.loads(raw_option)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "option_values 필드는 JSON 배열 형태여야 합니다."
                )
        else:
            option_data = None

        if option_data is not None:
            instance.option_values.all().delete()

            for option in option_data:
                category_name = option.get("category_input")
                extra_price = option.get("extra_price", 0)

                category = Category.objects.filter(name=category_name).first()
                if not category:
                    raise serializers.ValidationError(
                        f"옵션 카테고리 {category_name} 이(가) 존재하지 않습니다."
                    )

                ProductOptionValue.objects.create(
                    product=instance, category=category, extra_price=extra_price
                )

        images_data = request.FILES.getlist("images")
        # 이미지 처리
        if images_data is not None:
            # 기존 이미지 전부 삭제 후 추가
            instance.images.all().delete()
            for image_data in images_data:
                ProductImages.objects.create(product=instance, image_url=image_data)

        # stock sold_out 연동
        new_stock = validated_data.get("stock", instance.stock)
        instance.stock = new_stock
        instance.sold_out = new_stock <= 0

        return instance
