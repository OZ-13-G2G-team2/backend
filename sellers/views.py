from rest_framework import generics, permissions
from sellers.serializers import SellersSerializer

from sellers.models import Seller

class SellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellersSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'