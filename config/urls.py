from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    # products 앱 include
    path('api/products/', include('products.urls', namespace='products')),

]
