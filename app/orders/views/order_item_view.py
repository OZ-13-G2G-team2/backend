from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from app.orders.services.order_item_service import OrderItemService


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
    destroy=extend_schema(
        summary="주문상품 삭제", description="주문상품을 삭제합니다.", tags=["주문상품"]
    ),
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
            return Response(
                {"error": "product 필수"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not quantity or int(quantity) <= 0:
            return Response(
                {"error": "quantity 필수 또는 0보다 커야 함"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = int(quantity)
        item = OrderItemService.create_item(
            order=order,
            product_id=product.id,
            quantity=quantity,
            price_at_purchase=price_at_purchase,
        )

        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        quantity = request.data.get("quantity")
        if quantity is None or int(quantity) <= 0:
            return Response({"error": "quantity는 1 이상이어야 합니다."}, status=400)

        new_quantity = int(quantity)

        item = OrderItemService.update_quantity(item, new_quantity)
        return Response(self.get_serializer(item).data)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        OrderItemService.delete_item(item)
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
