from django.urls import path
from .views.order_item_view import OrderItemViewSet
from .views import OrderViewSet

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
        "order-items/",
        OrderItemViewSet.as_view({"get": "list", "post": "create"}),
        name="orderitem_list_create",
    ),
    path(
        "order-items/<int:pk>/",
        OrderItemViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="orderitem_detail",
    ),
]
