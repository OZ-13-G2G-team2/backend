from django.urls import path
from app.products import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListAPIView.as_view(), name="product-list"),
    path("create/", views.ProductCreateAPIView.as_view(), name="product-create"),
    path("search/", views.ProductSearchAPIView.as_view(), name="product-search"),
    path(
        "<int:product_id>/",
        views.ProductRetrieveUpdateDestroyAPIView.as_view(),
        name="product-detail",
    ),
    path(
        "<int:product_id>/stock/",
        views.ProductStockUpdateAPIView.as_view(),
        name="product-stock",
    ),
    path(
        "<int:product_id>/images/",
        views.ProductImageUploadAPIView.as_view(),
        name="product-image-upload",
    ),

]
