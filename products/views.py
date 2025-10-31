from rest_framework import generics, permissions
from products.models import Product
from .serializers import ProductSerializer


# 상품 목록 조회 + 등록
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def preform_create(self, serializer):
        serializer.save(seller_id=self.request.user.id)
