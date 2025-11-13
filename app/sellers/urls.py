from django.urls import path
from .views import SellerDetailView
from ..products.views import SellerProductsListAPIView

app_name = "sellers"

urlpatterns = [
    path("<int:pk>/", SellerDetailView.as_view(), name="seller-detail"),

    # 판매자 별 상품 목록 조회 (url 경로가 겹쳐서 부득이하게 이쪽으로 옮깁니다.)
    path(
        "products/<int:id>/",
        SellerProductsListAPIView.as_view(),
        name="seller-products-list",
    ),
]
