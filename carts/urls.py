from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register(r'apicarts', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
