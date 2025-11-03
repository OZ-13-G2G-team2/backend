from django.urls import path
from .views import SellerDetailView

app_name = "sellers"

urlpatterns = [
    path('<int:pk>/', SellerDetailView.as_view(), name='seller-detail'),
]
