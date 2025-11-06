from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action

from app.orders.models import OrderItem
from app.orders.serializers.order_item_serializer import OrderItemSerializer


@extend_schema_view(
    list=extend_schema(
        summary="주문상품 목록 조회",
        description="주문상품 목록을 조회합니다.",
        tags=["주문상품"],
    ),
    create=extend_schema(
        summary="주문상품 등록",
        description="새 주문상품을 등록합니다.",
        tags=["주문상품"],
    ),
    retrieve=extend_schema(
        summary="주문상품 상세 조회",
        description="주문상품 상세 정보를 조회합니다.",
        tags=["주문상품"],
    ),
    update=extend_schema(
        summary="주문상품 수정",
        description="주문상품 정보를 전체 수정합니다.",
        tags=["주문상품"],
    ),
    partial_update=extend_schema(
        summary="주문상품 부분 수정",
        description="주문상품 정보를 일부 수정합니다.",
        tags=["주문상품"],
    ),
    destroy=extend_schema(summary="주문상품 삭제", description="주문상품을 삭제합니다.", tags=["주문상품"]),
)
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request: Request = self.request
        queryset = OrderItem.objects.select_related("product", "order").all()
        order_id = request.query_params.get("order_id")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        else:
            queryset = queryset.filter(order__user=request.user)
        return queryset.order_by("-order__order_date")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        product = serializer.validated_data.get("product")
        quantity = serializer.validated_data.get("quantity")
        price_at_purchase = serializer.validated_data.get("price_at_purchase")

        if not product:
            return Response({"error": "product 필수"}, status=status.HTTP_400_BAD_REQUEST)
        if not quantity or int(quantity) <= 0:
            return Response(
                {"error": "quantity 필수 또는 0보다 커야 함"}, status=status.HTTP_400_BAD_REQUEST
            )

        quantity = int(quantity)

        if product.stock < quantity:
            return Response(
                {"error": f"재고 부족: {product.name}"}, status=status.HTTP_400_BAD_REQUEST
            )

        price_at_purchase = price_at_purchase or product.price

        product.stock -= quantity
        product.save(update_fields=["stock"])

        serializer.save(price_at_purchase=price_at_purchase)

        order.calculate_total()
        order.save(update_fields=["total_amount", "updated_at"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        new_quantity = request.data.get("quantity")
        change_reason = request.data.get("change_reason")

        if not change_reason:
            return Response(
                {"error": "변경 사유(change_reason)는 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_quantity_int = int(new_quantity)
            if new_quantity_int <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({"error": "잘못된 수량"}, status=status.HTTP_400_BAD_REQUEST)

        diff = new_quantity_int - item.quantity

        if diff > 0 and item.product.stock < diff:
            return Response(
                {"error": f"재고 부족: {item.product.name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.product.stock -= diff
        item.product.save(update_fields=["stock"])

        item.quantity = new_quantity_int
        item.change_reason = change_reason
        item.save(update_fields=["quantity", "change_reason", "updated_at"])

        item.order.calculate_total()
        item.order.save(update_fields=["total_amount", "updated_at"])

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.product.stock += item.quantity
        item.product.save(update_fields=["stock"])
        order = item.order
        item.delete()
        order.calculate_total()
        order.save(update_fields=["total_amount", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="by_order")
    def by_order(self, request):
        order_id = request.query_params.get("order_id")
        if not order_id:
            return Response(
                {"error": "order_id 필요"}, status=status.HTTP_400_BAD_REQUEST
            )

        items = OrderItem.objects.filter(order_id=order_id).select_related("product")
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
