from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from .models import Cart, CartItem
from .serializers import CartSerializer
from app.products.models import Product


@extend_schema(
    tags=["장바구니 관리"],
    summary="장바구니 관리",
    description="상품 담기, 조회, 수정, 삭제 기능",
)
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    # POST /api/carts/ : 단일 상품 추가
    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 추가",
        description="단일 상품을 장바구니에 추가",
    )
    def create(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not Product.objects.filter(id=product_id).exists():
            return Response({"error": "유효하지 않은 상품 ID"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=user)

        if CartItem.objects.filter(cart=cart, product_id=product_id).exists():
            return Response({"error": "이미 장바구니에 존재"}, status=409)

        CartItem.objects.create(cart=cart, product_id=product_id, quantity=quantity)
        return Response({"message": "상품이 장바구니에 추가되었습니다."}, status=200)

    # GET /api/carts/ : 본인 장바구니 조회
    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 조회",
        description="장바구니 상품 목록 조회",
    )
    def list(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "장바구니가 비어있음"}, status=404)

        serializer = CartSerializer(cart)
        return Response({"data": serializer.data}, status=200)

    # POST /api/carts/bulk_add/
    @extend_schema(
        tags=["장바구니 관리"],
        summary="여러 상품 추가",
        description="여러 상품을 장바구니에 추가",
    )
    @action(detail=False, methods=["post"], url_path="bulk_add")
    def bulk_add(self, request):
        user = request.user
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "상품 데이터 없음"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=user)
        duplicate, created = [], []

        for it in items:
            pid, qty = it.get("product_id"), it.get("quantity", 1)

            if not Product.objects.filter(id=pid).exists():
                return Response({"error": "유효하지 않은 상품 ID"}, status=400)

            if CartItem.objects.filter(cart=cart, product_id=pid).exists():
                duplicate.append(pid)
                continue

            CartItem.objects.create(cart=cart, product_id=pid, quantity=qty)
            created.append(pid)

        if duplicate:
            return Response({"error": "일부 상품이 이미 장바구니에 존재합니다."}, status=409)

        return Response({"message": "여러 상품이 장바구니에 추가되었습니다."}, status=200)

    # PATCH /api/carts/items/
    # DELETE /api/carts/items/
    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 상품 변경·삭제",
        description=(
            "PATCH: product_id 기반 수량 변경(부분 수정)\n"
            "DELETE: product_ids 배열 기반 선택 삭제 / 비어있으면 전체 삭제"
        ),
    )
    @action(detail=False, methods=["patch", "delete"], url_path="items")
    def items(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "장바구니 없음"}, status=404)

        # --- PATCH: 수량 부분 수정 ---
        if request.method == "PATCH":
            product_id = request.data.get("product_id")
            if product_id is None:
                return Response({"error": "product_id 필요"}, status=400)

            quantity = request.data.get("quantity", None)

            try:
                item = CartItem.objects.get(cart=cart, product_id=product_id)
            except CartItem.DoesNotExist:
                return Response({"error": "해당 상품 없음"}, status=404)

            if quantity is not None:
                item.quantity = quantity
                item.save()

            return Response({"message": "수정 완료"}, status=200)

        # --- DELETE: 선택/전체 삭제 ---
        if request.method == "DELETE":
            product_ids = request.data.get("product_ids", None)

            # 전체 삭제
            if product_ids is None:
                CartItem.objects.filter(cart=cart).delete()
                return Response({"message": "장바구니 전체 삭제 완료"}, status=200)

            # 선택 삭제
            if not isinstance(product_ids, list):
                return Response({"error": "product_ids는 배열이어야 합니다."}, status=400)

            deleted_count, _ = CartItem.objects.filter(
                cart=cart, product_id__in=product_ids
            ).delete()

            return Response({"message": f"{deleted_count}개 삭제 완료"}, status=200)
        return None
