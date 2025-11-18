from django.urls import path
from .views.order_item_view import OrderItemViewSet
from .views.order_view import OrderViewSet

app_name = "orders"

urlpatterns = [
    path(
        "",
        OrderViewSet.as_view({"get": "list", "post": "create"}),
        name="order_list_create",
    ),
    path(
        "<int:pk>/",
        OrderViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="order_detail",
    ),
    path(
        "<int:pk>/status/",
        OrderViewSet.as_view({"patch": "update_status"}),
        name="order_update_status",
    ),
    path(
        "items/",
        OrderItemViewSet.as_view({"get": "list", "post": "create"}),
        name="orderitem_list_create",
    ),
    path(
        "items/<int:pk>/",
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
    path(
        "items/by_order/",
        OrderItemViewSet.as_view({"get": "by_order"}),
        name="orderitem_list_by_order",
    ),
    path("buy-now/", OrderViewSet.as_view({"post": "buy_now"}), name="order_buy_now"),
    path(
        "cart-purchase/",
        OrderViewSet.as_view({"post": "cart_purchase"}),
        name="order_cart_purchase",
    ),
]
