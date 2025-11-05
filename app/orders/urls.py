from django.urls import path
from .views.order_item_view import OrderItemViewSet
from .views.order_view import OrderViewSet

app_name = "orders"

urlpatterns = [
    path(
        "orders/",
        OrderViewSet.as_view({"get": "list", "post": "create"}),
        name="order_list_create",
    ),
    path(
        "orders/<int:pk>/",
        OrderViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="order_detail",
    ),
    path(
        "orders/<int:pk>/status/",
        OrderViewSet.as_view({"patch": "update_status"}),
        name="order_update_status",
    ),
    path(
        "order_items/",
        OrderItemViewSet.as_view({"get": "list", "post": "create"}),
        name="orderitem_list_create",
    ),
    path(
        "order_items/<int:pk>/",
        OrderItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="orderitem_detail",
    ),
]
