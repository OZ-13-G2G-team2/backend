from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers.order_serializer import OrderSerializer
from orders.serializers.order_item_serializer import OrderItemSerializer
from orders.services import OrderService


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-order_date")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-order_date")

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.calculate_total()

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.select_related("product").all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """주문 상태 변경"""
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
