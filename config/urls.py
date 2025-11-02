from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', 메인 페이지)
    # users 앱 include
    path('api/users/', include('users.urls', namespace='users')),
    #sellers 앱 include
    path('api/sellers/', include('sellers.urls', namespace='sellers')),
    #products 앱 include
    path('api/products/', include('products.urls', namespace='products')),
    # reviews 앱 include
    path("api/reviews/", include("reviews.urls")),
    # orders 앱 include
    path("api/orders/", include("orders.urls", namespace="orders")),



    # 스키마 자동 생성
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
