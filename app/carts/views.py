from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer
from app.products.models import Product
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["장바구니 관리"],
    summary = "장바구니 추가",
    description = "상품을 장바구니에 담고 보관 조회하는 기능",
)
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    # POST /api/carts/ : 장바구니 추가
    def create(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not Product.objects.filter(id=product_id).exists():
            return Response(
                {"error": "유효하지 않은 상품 ID가 존재합니다."}, status=400
            )

        cart, _ = Cart.objects.get_or_create(user=user)
        if CartItem.objects.filter(cart=cart, product_id=product_id).exists():
            return Response({"error": "이미 장바구니에 존재"}, status=409)

        CartItem.objects.create(cart=cart, product_id=product_id, quantity=quantity)
        return Response({"message": "상품이 장바구니에 추가되었습니다."}, status=200)

    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 조회",
        description="장바구니에 있는 상품목록 조회",
    )
    # GET /api/carts/?user_id={id} : 장바구니 조회
    def list(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id 필요"}, status=400)

        try:
            cart = Cart.objects.get(user_id=user_id)
        except Cart.DoesNotExist:
            return Response({"error": "장바구니가 비어있음"}, status=404)

        serializer = CartSerializer(cart)
        return Response({"data": serializer.data}, status=200)

    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 변경",
        description="장바구니에 있는 상품 수량 변경",
    )
    # PUT /api/carts/{cart_item_id}/ : 수량 변경
    def update(self, request, pk=None):
        try:
            item = CartItem.objects.get(id=pk)
        except CartItem.DoesNotExist:
            return Response({"error": "잘못된 수량"}, status=400)

        item.quantity = request.data.get("quantity", item.quantity)
        item.save()
        return Response({"message": "수정이 완료되었습니다."}, status=200)

    @extend_schema(
        tags=["장바구니 관리"],
        summary="장바구니 삭제 ",
        description="장바구니에 있는 상품 삭제",
    )
    # DELETE /api/carts/{cart_item_id}/ : 장바구니 상품 삭제
    def destroy(self, request, pk=None):
        try:
            item = CartItem.objects.get(id=pk)
        except CartItem.DoesNotExist:
            return Response({"error": "항목 없음"}, status=404)

        item.delete()
        return Response({"message": "상품이 삭제되었습니다."}, status=200)

    @extend_schema(
        tags=["장바구니 관리"],
        summary="여러상품 추가",
        description="여러상품을 장바구니에 추가",
    )
    # POST /api/carts/bulk/ : 여러 상품 추가
    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_add(self, request):
        user = request.user
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "상품 데이터 없음"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=user)
        created, duplicate = [], []

        for it in items:
            pid, qty = it.get("product_id"), it.get("quantity", 1)
            if not Product.objects.filter(id=pid).exists():
                return Response(
                    {"error": "유효하지 않은 상품 ID가 존재합니다."}, status=400
                )
            if CartItem.objects.filter(cart=cart, product_id=pid).exists():
                duplicate.append(pid)
                continue
            CartItem.objects.create(cart=cart, product_id=pid, quantity=qty)
            created.append(pid)

        if duplicate:
            return Response(
                {"error": "일부 상품이 이미 장바구니에 존재합니다."}, status=409
            )

        return Response({"message": "상품이 장바구니에 추가되었습니다."}, status=200)
