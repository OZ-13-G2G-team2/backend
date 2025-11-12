from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
from app.products.models import Product
from rest_framework.permissions import IsAdminUser

from app.orders.models import Order
from app.orders.serializers.order_serializer import OrderSerializer
from app.orders.serializers.order_item_serializer import OrderItemSerializer
from app.orders.services.order_item_service import OrderItemService
from app.orders.services import OrderService
from app.orders.exceptions import OrderNotFound, InvalidOrderStatus
from app.carts.models import CartItem

from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(summary="주문 목록 조회", tags=["주문"]),
    create=extend_schema(summary="주문 등록", tags=["주문"]),
    retrieve=extend_schema(summary="주문 상세 조회", tags=["주문"]),
    update=extend_schema(summary="주문 수정", tags=["주문"]),
    destroy=extend_schema(summary="주문 삭제", tags=["주문"]),
    update_status=extend_schema(summary="주문 상태 변경", tags=["주문"]),
    items=extend_schema(summary="주문 상품 조회", tags=["주문"]),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-order_date")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Order.objects.filter(user=user)
            .select_related()
            .prefetch_related("items__product")
            .order_by("-order_date")
        )

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
                product_id=cart_item.product.id,
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
        address = request.data.get("address")
        payment_method = request.data.get("payment_method")

        if not product_id or not address or not payment_method:
            return Response(
                {"error": "상품 ID, 주소, 결제 수단은 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.select_for_update().get(id=product_id)
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
            status="pending",
            total_amount=0,
        )

        OrderItemService.create_item(
            order=order,
            product_id=product.id,
            quantity=quantity,
            price_at_purchase=product.price,
        )

        order.calculate_total()
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAdminUser]
    )
    def update_status(self, request, pk=None):

        order = self.get_object()
        new_status = request.data.get("status")
        update_note = request.data.get("update_note", "")

        try:
            updated_order = OrderService.update_status(order.id, new_status, user=request.user)
        except OrderNotFound:
            return Response(
                {"error": "주문을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidOrderStatus:
            return Response(
                {"error": "잘못된 주문 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "order_id": updated_order.id,
                "status": updated_order.status,
                "status_display": updated_order.get_status_display(),
                "updated_at": updated_order.updated_at,
                "update_note": update_note,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_order(self, request, pk=None):

        order = self.get_object()
        if order.user != request.user:
            return Response({"error": "권한이 없습니다."}, status=403)
        if order.status not in ["pending", "completed"]:
            return Response({"error": "취소할 수 없는 상태입니다."}, status=400)

        order.status = "cancelled"
        order.save(update_fields=["status"])
        return Response({"message": "주문이 취소되었습니다.", "status": order.status})

