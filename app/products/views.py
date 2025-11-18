from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, serializers, filters
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductStockSerializer,
    ProductImagesSerializer,
    ProductForSellerSerializer,
    ProductDetailWithSellerSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)
from .models import Product, Category, CategoryGroup, ProductImages
from django.http.response import Http404
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app.sellers.models import Seller


# 상품 목록 조회 및 검색
@extend_schema(
    tags=["상품 목록 / 검색"],
    summary="목록 조회 및 검색",
    description="검색 필터 : 검색어, 원산지, 카테고리, 가격 범위, 품절 여부, 판매자, 해외배송 여부 등을 필터링 가능. "
    "정렬 키워드 : sale_price, sales_count, review_count, wish_count, discount_price, created_at",
    parameters=[
        OpenApiParameter("q", str, description="검색어"),
        OpenApiParameter("origin", str, description="원산지"),
        OpenApiParameter("category_name", str, description="카테고리 이름"),
        OpenApiParameter("min_price", float, description="최소 가격"),
        OpenApiParameter("max_price", float, description="최대 가격"),
        OpenApiParameter("sold_out", str, description="품절 여부 (true/false)"),
        OpenApiParameter("seller_id", int, description="판매자 id"),
        OpenApiParameter("seller_business_name", str, description="사업자 명"),
        OpenApiParameter(
            "overseas_shipping", str, description="해외배송 여부 (true/false)"
        ),
    ],
)
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "price",
        "discount_price",
        "stats__review_count",
        "stats__sales_count",
        "stats__wish_count",
        "created_at",
    ]
    ordering = "-stats__review_count"
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.select_related("stats").all()
        params = self.request.query_params

        q = params.get("q", "").strip()
        origin = params.get("origin")
        category_name = params.get("category_name")
        sold_out = params.get("sold_out")
        seller_id = params.get("seller_id")
        seller_business_name = params.get("seller_business_name")
        overseas_shipping = params.get("overseas_shipping")

        try:
            min_price = float(params.get("min_price", 0))
        except ValueError:
            min_price = 0
        try:
            max_price = float(params.get("max_price", 0))
        except ValueError:
            max_price = 0

        my_filters = Q()

        # 검색어 기반
        if q:
            my_filters &= (
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(origin__icontains=q)
                | Q(categories__name__icontains=q)
            )

        # 원산지 필터
        if origin:
            my_filters &= Q(origin__iexact=origin)

        # 카테고리 필터
        if category_name:
            my_filters &= Q(categories__name__icontains=category_name)

        # 가격 범위 필터
        if min_price:
            my_filters &= Q(price__gte=min_price)
        if max_price:
            my_filters &= Q(price__lte=max_price)

        # 품절 여부 필터
        if sold_out is not None:
            sold_out_value = sold_out.lower() == "true"
            my_filters &= Q(sold_out=sold_out_value)

        # 판매자 아이디 필터
        if seller_id:
            seller_id = int(seller_id)
            my_filters &= Q(seller__id=seller_id)

        # 판매자 필터
        if seller_business_name:
            my_filters &= Q(seller__business_name__icontains=seller_business_name)

        # 해외배송 여부 필터
        if overseas_shipping is not None:
            overseas_shipping_value = str(overseas_shipping).lower() == "true"
            my_filters &= Q(overseas_shipping=overseas_shipping_value)

        queryset = queryset.filter(my_filters).distinct()

        queryset = queryset.annotate(
            sales_count=Count("order_items", distinct=True),
            review_count=Count("review", distinct=True),
            wish_count=Count("wishlists", distinct=True),
        )

        return queryset.order_by("-sales_count", "-created_at")


# 상품 등록
@extend_schema(
    tags=["상품 등록"],
    summary="상품 등록",
    description="새로운 상품 등록 가능",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "상품명"},
                "origin": {"type": "string", "description": "원산지"},
                "stock": {"type": "integer", "description": "재고"},
                "price": {"type": "number", "description": "가격"},
                "discount_price": {"type": "number", "description": "할인 가격"},
                "overseas_shipping": {
                    "type": "boolean",
                    "description": "해외 배송 여부",
                    "default": False,
                },
                "delivery_fee": {"type": "number", "description": "운송비"},
                "description": {"type": "string", "description": "상품 설명"},
                "sold_out": {
                    "type": "boolean",
                    "description": "품절 여부",
                    "default": False,
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "1: 시즌(1-4) / 2: 테마(5-14) / 3: 색상(15-19) / 4: 사이즈(20-23) / 5: kg(24-32) ",
                },
                "option_values": {
                    "type": "string",
                    "description": "색상(빨강 노랑 초록 파랑 검정) / 사이즈(소 중 대 특대) / kg(500g 1kg 2kg 3kg 4kg 5kg 7kg 10kg 20kg)",
                    "example": '[{"category_input": "특대", "extra_price": 3000},'
                    '{"category_input": "빨강", "extra_price": 0},'
                    '{"category_input": "10kg", "extra_price": 5000}]',
                },
                "images": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                },
            },
            "required": ["name", "origin", "price"],
        }
    },
    responses=ProductCreateSerializer,
)
class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return Response(
                {"error": "인증이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            seller = Seller.objects.get(user=user)
        except Seller.DoesNotExist:
            return Response(
                {"error": "판매자 계정이 아닙니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            product = serializer.save(seller=seller)
        except serializers.ValidationError as e:
            return Response(
                {"error": "잘못된 입력입니다.", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        image_files = request.FILES.getlist("images")
        if image_files:
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

            for image in image_files:
                if not image or not hasattr(image, "name"):
                    return Response(
                        {"error": "유효하지 않은 이미지 파일입니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not any(
                    image.name.lower().endswith(ext) for ext in valid_extensions
                ):
                    return Response(
                        {"error": f"{image.name}은(는) 올바르지 않은 확장자입니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ProductImages.objects.create(
                    product=product, user=user, image_url=image
                )

        headers = self.get_success_headers(serializer.data)
        product.refresh_from_db()
        return Response(
            ProductDetailWithSellerSerializer(product).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


@extend_schema(tags=["상품 상세 / 수정 / 삭제"])
# 상품 상세페이지 / 수정 / 삭제
class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete"]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Product.objects.all()
    lookup_field = "product_id"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProductUpdateSerializer
        return ProductDetailWithSellerSerializer

    @extend_schema(
        summary="상품 상세 조회",
        description="상품의 아이디를 입력하면 그 상품의 상세 데이터 조회 가능",
    )
    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": "해당 상품을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        summary="상품 수정",
        description="상품의 아이디를 입력하고 그 상품의 상세 데이터 수정 가능",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "상품명"},
                    "origin": {"type": "string", "description": "원산지"},
                    "stock": {"type": "integer", "description": "재고 수량"},
                    "price": {"type": "number", "description": "정상가"},
                    "discount_price": {"type": "number", "description": "할인가"},
                    "overseas_shipping": {
                        "type": "boolean",
                        "description": "해외 배송 여부",
                        "default": False,
                    },
                    "delivery_fee": {"type": "number", "description": "배송비"},
                    "description": {"type": "string", "description": "상품 설명"},
                    "sold_out": {
                        "type": "boolean",
                        "description": "품절 여부",
                        "default": False,
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "1: 시즌(1-4) / 2: 테마(5-14) / 3: 색상(15-19) / 4: 사이즈(20-23) / 5: kg(24-32)",
                    },
                    "option_values": {
                        "type": "string",
                        "description": "색상(빨강 노랑 초록 파랑 검정) / 사이즈(소 중 대 특대) / kg(500g 1kg 2kg 3kg 4kg 5kg 7kg 10kg 20kg)",
                        "example": '[{"category_input": "특대", "extra_price": 3000},'
                        '{"category_input": "빨강", "extra_price": 0},'
                        '{"category_input": "10kg", "extra_price": 5000}]',
                    },
                    "images": {
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                        "description": "상품 이미지 파일들",
                    },
                    "seller_username": {"type": "string", "readOnly": True},
                    "seller_business_name": {"type": "string", "readOnly": True},
                    "seller_business_number": {"type": "string", "readOnly": True},
                },
                "required": ["name", "origin", "price"],
            }
        },
        responses=ProductUpdateSerializer,
    )
    def patch(self, request, *args, **kwargs):
        try:
            product = self.get_object()
        except Http404:
            return Response(
                {"detail": "해당 상품을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = self.request.user
        if product.seller.user.email != user.email:
            return Response(
                {"error": "인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"error": "잘못된 입력입니다.", "detail": serializer.errors},
            )

        product = serializer.save()

        image_files = request.FILES.getlist("images")
        if image_files:
            product.images.all().delete()
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

            for image in image_files:
                if not any(
                    image.name.lower().endswith(ext) for ext in valid_extensions
                ):
                    return Response(
                        {"error": f"{image.name}은(는) 올바르지 않은 확장자입니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ProductImages.objects.create(product=product, image_url=image)
        return Response(
            ProductDetailWithSellerSerializer(product).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="상품 삭제", description="상품의 아이디를 입력하고 그 상품을 삭제"
    )
    def delete(self, request, *args, **kwargs):
        try:
            product = self.get_object()
        except Http404:
            return Response(
                {"detail": "해당 상품을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = self.request.user
        if not product.seller.user.email == user.email:
            return Response(
                {"error": "인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["카테고리를 확인"],
    summary="카테고리 리스트 확인",
    description="1: 시즌(1-4) / 2: 테마(5-14) / 3: 색상(15-19) / 4: 사이즈(20-23) / 5: kg(24-32) / 카테고리 실제 사용시 입력 예시: 1,2 = 시즌-여름",
)
class CategoryByGroupAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        group_id = self.kwargs["group_id"]

        if not CategoryGroup.objects.filter(id=group_id).exists():
            raise Http404("해당 카테고리는 존재하지 않습니다.")

        return Category.objects.filter(group_id=group_id).order_by("id")


@extend_schema(
    tags=["카테고리별 상품 조회"],
    summary="카테고리별 상품 조회",
    description="특정 카테고리 아이디를 기준으로 상품을 조회합니다.",
)
class ProductsByCategoryAPIView(generics.ListAPIView):
    serializer_class = ProductForSellerSerializer

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        if not Category.objects.filter(id=category_id).exists():
            raise Http404("해당 카테고리는 존재하지 않습니다.")
        return Product.objects.filter(
            categories__id=category_id, sold_out=False
        ).order_by("-created_at")


@extend_schema(tags=["상품 재고 업데이트"], summary="상품 재고 업데이트")
class ProductStockUpdateAPIView(generics.UpdateAPIView):
    http_method_names = ["put"]
    queryset = Product.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "product_id"

    def put(self, request, *args, **kwargs):
        product = self.get_object()

        user = self.request.user
        if product.seller.user.email != user.email:
            return Response(
                {"error": "인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# 이미지 등록 view
@extend_schema(
    tags=["이미지 등록"],
    summary="상품 이미지 업로드",  # 요약 추가
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "product": {"type": "integer"},
                "user": {"type": "integer"},
                "image_url": {"type": "string", "format": "binary"},
            },
            "required": ["product", "user", "image_url"],
        }
    },
    responses=ProductImagesSerializer,
)
class ProductImageUploadAPIView(generics.CreateAPIView):
    serializer_class = ProductImagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, product_id=product_id)
        user = self.request.user

        if product.seller.user.email != user.email:
            return Response(
                {"error": "인증이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        image = self.request.data.get("image_url")
        if not image:
            return Response(
                {"error": "이미지 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
            return Response(
                {"error": "올바르지 않은 확장자입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=self.request.user, image_url=image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 판매자 상품 목록
@extend_schema(
    tags=["판매자별 상품 목록 조회"],
    summary="판매자별 상품 목록 조회",
    description="정렬 키워드 : sale_price, sales_count, review_count, wish_count, created_at",
)
class SellerProductsListAPIView(generics.ListAPIView):
    serializer_class = ProductForSellerSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "sale_price",
        "sales_count",
        "review_count",
        "wish_count",
        "discount_rate",
        "created_at",
    ]
    ordering = ["-sales_count", "-created_at"]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        seller_id = self.kwargs.get("id")
        try:
            seller = Seller.objects.get(pk=seller_id)  # noqa: F841
        except Seller.DoesNotExist:
            raise Http404("요청한 판매자가 존재하지 않습니다.")

        queryset = (
            Product.objects.filter(seller=seller)
            .annotate(
                sales_count=Count("order_items", distinct=True),
                review_count=Count("review", distinct=True),
                wish_count=Count("wishlists", distinct=True),
            )
            .order_by("-sales_count", "-created_at")
        )

        return queryset
