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
)
from .models import Product, Category, CategoryGroup
from django.http.response import Http404
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from sellers.models import Seller


# 상품 목록 조회 + 등록
@extend_schema(tags=["상품 목록 조회 / 등록"], summary="목록 조회 및 등록")
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["price"]
    ordering = ("-created_at",)

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        request = self.request
        if not request.user.is_authenticated:
            return Response(
                {"error": "인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(seller=request.user)

        except serializers.ValidationError as e:
            return Response({"error": "잘못된 입력입니다.", "details": e.detail})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@extend_schema(tags=["상품 상세 / 수정 / 삭제"])
# 상품 상세페이지 / 수정 / 삭제
class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "product_id"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(summary="상품 상세 조회")
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

    @extend_schema(summary="상품 수정")
    def put(self, request, *args, **kwargs):
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

        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"error": "잘못된 입력입니다."}, status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(summary="상품 삭제")
    def delete(self, request, *args, **kwargs):
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

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["카테고리"], summary="카테고리 관련")
class CategoryByGroupAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        group_id = self.kwargs["group_id"]

        if not CategoryGroup.objects.filter(id=group_id).exists():
            raise Http404("해당 카테고리는 존재하지 않습니다.")

        return Category.objects.filter(group_id=group_id).order_by("id")


@extend_schema(tags=["상품 재고 업데이트"], summary="상품 재고 업데이트")
class ProductStockUpdateAPIView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    queryset = Product.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "product_id"

    def patch(self, request, *args, **kwargs):
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
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'product': {'type': 'integer'},
                'user': {'type': 'integer'},

                'image_url': {
                    'type': 'string',
                    'format': 'binary'
                }
            },
            'required': ['product', 'user', 'image_url']
        }
    },
    responses=ProductImagesSerializer
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


# 검색
@extend_schema(tags=["검색 기능"], summary="상품 검색", description="범위: 검색어,원산지,카테고리,최소금액&최대금액 필터,품절아닌 상품,판매자")
class ProductSearchAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        params = self.request.query_params

        q = params.get("q", "")
        origin = params.get("origin")
        category_id = params.get("category_id")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        sold_out = params.get("sold_out")
        seller = params.get("seller")
        overseas_shipping = params.get("overseas_shipping")

        my_filters = Q()

        # 검색어 기반
        if q:
            my_filters &= (
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(origin__icontains=q)
                | Q(categories__icontains=q)
            )

        # 원산지 필터
        if origin:
            my_filters &= Q(origin_iexact=origin)

        # 카테고리 필터
        if category_id:
            my_filters &= Q(categories__id__icontains=category_id) & Q(
                categories__group=2
            )

        # 가격 범위 필터
        if min_price:
            my_filters &= Q(price__gte=min_price)
        if max_price:
            my_filters &= Q(price__lte=max_price)

        # 품절 여부 필터
        if sold_out is not None:
            sold_out_value = sold_out.lower() == "true"
            my_filters &= Q(sold_out=sold_out_value)

        # 판매자 필터
        if seller:
            my_filters &= Q(seller_id=seller)

        # 해외배송 여부 필터
        if overseas_shipping is not None:
            overseas_value = overseas_shipping.lower() == "true"
            my_filters &= Q(overseas_value=overseas_value)

        return queryset.filter(my_filters).distinct()


# 판매자 상품 목록
@extend_schema(tags=["판매자별 상품 목록 조회"])
class SellerProductsListAPIView(generics.ListAPIView):
    serializer_class = ProductForSellerSerializer

    def get_queryset(self):
        seller_id = self.kwargs.get("id")
        try:
            seller = Seller.objects.get(id=seller_id)
        except Seller.DoesNotExist:
            raise Http404("요청한 판매자가 존재하지 않습니다.")
        return Product.objects.filter(seller_id=seller_id)

