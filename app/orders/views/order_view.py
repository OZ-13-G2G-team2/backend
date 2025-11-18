from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view

from app.address.models import Address
from app.orders.models import Order
from app.orders.serializers.order_serializer import (
    OrderSerializer,
    CartPurchaseOrderSerializer,
)
from app.orders.serializers.order_item_serializer import OrderItemSerializer
from app.orders.services.order_item_service import OrderItemService
from app.orders.services import OrderService
from app.orders.exceptions import OrderNotFound, InvalidOrderStatus
from app.carts.models import CartItem
from app.products.models import Product, ProductStats


@extend_schema_view(
    list=extend_schema(summary="주문 목록 조회", tags=["주문"]),
    create=extend_schema(summary="주문 등록", tags=["주문"]),
    retrieve=extend_schema(summary="주문 상세 조회", tags=["주문"]),
    update=extend_schema(summary="주문 수정", tags=["주문"]),
    destroy=extend_schema(summary="주문 삭제", tags=["주문"]),
    update_status=extend_schema(summary="주문 상태 변경", tags=["주문"]),
    items=extend_schema(summary="주문 상품 조회", tags=["주문"]),
    buy_now=extend_schema(summary="주문 즉시 구매", tags=["주문"]),
    cart_purchase=extend_schema(summary="장바구니 구매", tags=["주문"]),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-order_date")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-order_date")

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        order = serializer.save(user=user)
        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items.exists():
            raise ValidationError("장바구니가 비어 있습니다.")

        for cart_item in cart_items:
            OrderItemService.create_item(
                order=order,
                product_id=cart_item.product.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price,
            )
        cart_items.delete()
        order.calculate_total()
        order.save()

    @action(detail=False, methods=["post"], url_path="buy-now")
    @transaction.atomic
    def buy_now(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        address_id = request.data.get("address_id")
        payment_method = request.data.get("payment_method")

        if not product_id or not address_id or not payment_method:
            return Response(
                {"error": "상품 ID, 주소, 결제 수단은 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response(
                {"error": "존재하지 않는 주소입니다."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            product = Product.objects.select_for_update().get(product_id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "존재하지 않는 상품입니다."}, status=status.HTTP_404_NOT_FOUND
            )

        if product.stock < quantity:
            return Response(
                {"error": "재고가 부족합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            user=user,
            address=address,
            payment_method=payment_method,
            total_amount=product.price * quantity,
            status="pending",
        )

        OrderItemService.create_item(
            order,
            product_id=product.product_id,
            quantity=quantity,
            price_at_purchase=product.price,
        )

        product.refresh_from_db()
        order.calculate_total()
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="cart-purchase")
    @transaction.atomic
    def cart_purchase(self, request):
        user = request.user
        address_id = request.data.get("address_id")
        payment_method = request.data.get("payment_method")

        # 필수 값 확인
        if not address_id or not payment_method:
            return Response(
                {"error": "주소와 결제 수단은 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 주소 존재 여부 확인
        try:
            Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response(
                {"error": "존재하지 않는 주소입니다."}, status=status.HTTP_404_NOT_FOUND
            )

        # Order 생성 + 장바구니 처리
        serializer = CartPurchaseOrderSerializer(
            data={"address_id": address_id, "payment_method": payment_method},
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
            order = OrderService.create_order_from_cart(user, serializer)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            message = e.detail

            if isinstance(message, dict):
                message = list(message.values())[0]
                if isinstance(message, list):
                    message = message[0]

            elif isinstance(message, list):
                message = message[0]

            if hasattr(message, "code"):
                message = str(message)

            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response(
                {"error": "이 주문에 접근할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        items = order.items.select_related("product").all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get("status")
        update_note = request.data.get("update_note", "")

        try:
            updated_order = OrderService.update_status(
                order.id, new_status, user=request.user
            )
        except OrderNotFound:
            return Response(
                {"error": "주문을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        except InvalidOrderStatus:
            return Response(
                {"error": "잘못된 주문 상태입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "order_id": updated_order.id,
                "status": updated_order.status,
                "updated_at": updated_order.updated_at,
                "update_note": update_note,
            },
            status=status.HTTP_200_OK,
        )
