from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import OrderItem
from orders.serializers.order_item_serializer import OrderItemSerializer
from orders.services.order_item_service import OrderItemService


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            OrderItem.objects.filter(order__user=self.request.user)
            .select_related("product", "order")
            .order_by("-order__order_date")
        )

    def partial_update(self, request, pk=None):
        item = self.get_object()
        new_quantity = request.data.get("quantity")
        if new_quantity is None or int(new_quantity) <= 0:
            return Response(
                {"error": "잘못된 수량"}, status=status.HTTP_400_BAD_REQUEST
            )

        if new_quantity is None or int(new_quantity) <= 0:
            return Response(
                {"error": "잘못된 수량"}, status=status.HTTP_400_BAD_REQUEST
            )
        change_reason = request.data.get("change_reason", "")
        previous_quantity = item.quantity
        updated_item = OrderItemService.update_quantity(
            item.id, int(new_quantity), user=request.user
        )

        return Response(
            {
                "order_item_id": updated_item.id,
                "product_id": updated_item.product.id,
                "product_name": updated_item.product.name,
                "previous_quantity": previous_quantity,
                "updated_quantity": updated_item.quantity,
                "change_reason": change_reason,
                "updated_at": updated_item.order.updated_at,
                "message": "주문상품 정보가 수정되었습니다.",
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        OrderItemService.delete_item(item.id, user=request.user)
        return Response(
            {
                "order_item_id": item.id,
                "message": "주문상품이 성공적으로 삭제되었습니다.",
            },
            status=status.HTTP_200_OK,
        )
