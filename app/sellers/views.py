from rest_framework import generics, permissions
from app.sellers.serializers import SellersSerializer

from app.sellers.models import Seller
from drf_spectacular.utils import extend_schema


# 판매자 상세조회
@extend_schema(tags=["판매자 상세"])
class SellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellersSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
