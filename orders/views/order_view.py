from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order,OrderItem
from orders.serializers.order_serializer import OrderSerializer
from orders.serializers.order_item_serializer import OrderItemSerializer
from orders.services import OrderService
from products.models import Product



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

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order_items_data = self.request.data.get("items", [])

        for item in order_items_data:
            try:
                product = Product.objects.get(id=item["product_id"])
            except Product.DoesNotExist:
                raise ValueError(f"존재하지 않는 상품: {item['product_id']}")

            quantity = item.get("quantity", 0)
            if quantity <= 0:
                raise ValueError(f"잘못된 수량: {quantity}")

            price_at_purchase = item.get("price_at_purchase") or product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )

        order.calculate_total()

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
