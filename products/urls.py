from django.urls import path
from .views import ProductListCreateAPIView

from products import views

app_name = "products"

urlpatterns = [
     path('',views.ProductListCreateAPIView.as_view(), name='product_list'),


]
