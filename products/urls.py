from django.urls import path
from products import views

app_name = "products"

urlpatterns = [
    path('',views.ProductListCreateAPIView.as_view(), name='product_list'),
    path('{product_id}/', views.ProductDetailAPIView.as_view(), name='product_detail'),


]
