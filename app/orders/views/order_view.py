from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from app.orders.services.order_item_service import OrderItemService

from app.orders.models import Order, OrderItem
from app.orders.serializers.order_serializer import OrderSerializer
from app.orders.serializers.order_item_serializer import OrderItemSerializer
from app.orders.services import OrderService
from app.products.models import Product
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(
        summary="주문 목록 조회",
        description="사용자의 주문 목록을 조회합니다.",
        tags=["주문"],
    ),
    create=extend_schema(summary="주문 등록", description="새 주문을 등록합니다.", tags=["주문"]),
    retrieve=extend_schema(
        summary="주문 상세 조회",
        description="주문 상세 정보를 조회합니다.",
        tags=["주문"],
    ),
    update=extend_schema(summary="주문 수정", description="주문 정보를 전체 수정합니다.", tags=["주문"]),
    destroy=extend_schema(summary="주문 삭제", description="주문을 삭제합니다.", tags=["주문"]),
    update_status=extend_schema(
        summary="주문 상태 변경", description="주문의 상태를 변경합니다.", tags=["주문"]
    ),
    items=extend_schema(
        summary="주문 상품 조회",
        description="주문에 포함된 상품 목록을 조회합니다.",
        tags=["주문"],
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-order_date")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.all().order_by("-order_date")
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        items = self.request.data.get("items", [])

        if not items:
            raise ValueError("주문 상품이 비어 있습니다.")

        for item in items:
            OrderItemService.create_item(
                order=order,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price_at_purchase=item.get("price_at_purchase"),
            )

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.select_related("product").all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        update_note = request.data.get("update_note", "")

        try:
            updated_order = OrderService.update_status(
                order.id, new_status, user=request.user
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "order_id": updated_order.id,
                "status": updated_order.status,
                "updated_at": updated_order.updated_at,
                "update_note": update_note,
            },
            status=status.HTTP_200_OK,
        )
