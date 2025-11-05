from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from config.settings import base, dev, prod
from app.products.views import CategoryByGroupAPIView, SellerProductsListAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', 메인 페이지)
    # users 앱 include
    path("api/users/", include("app.users.urls", namespace="users")),
    # sellers 앱 include
    path("api/sellers/", include("app.sellers.urls", namespace="sellers")),
    # products 앱 include
    path("api/products/", include("app.products.urls", namespace="products")),
    path("api/products/", include("products.urls", namespace="products")),
    # carts 앱 include
    path("api/carts/", include("carts.urls")),
    # reviews 앱 include
    path("api/reviews/", include("app.reviews.urls")),
    path("api/reviews/", include("reviews.urls", namespace="reviews")),
    # Wishlists 앱 include
    path("api/wishlists/", include("wishlists.urls", namespace="wishlists")),
    # orders 앱 include
    path("api/orders/", include("app.orders.urls", namespace="orders")),
    # 카테고리 관련
    path(
        "api/categories/group/<int:group_id>/",
        CategoryByGroupAPIView.as_view(),
        name="category-by-group",
    ),
    # 판매자 별 상품 목록 조회
    path(
        "api/sellers/<int:id>/products/",
        SellerProductsListAPIView.as_view(),
        name="seller-products-list",
    ),
    # 스키마 자동 생성
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Redoc UI
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# 디버그 툴 바
if dev.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
