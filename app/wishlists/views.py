from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Wishlist
from .serializers import WishlistSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["찜목록 조회"])
class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        if Wishlist.objects.filter(user=user, product_id=product_id).exists():
            return Response({"error": "이미 존재"}, status=status.HTTP_400_BAD_REQUEST)

        wishlist = Wishlist.objects.create(user=user, product_id=product_id)
        return Response(
            {"message": "위시리스트에 추가되었습니다."}, status=status.HTTP_200_OK
        )

    def get(self, request):
        user = request.user
        wishlists = Wishlist.objects.filter(user=user)
        serializer = WishlistSerializer(wishlists, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class WishlistDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, wish_id):
        wishlist = get_object_or_404(Wishlist, id=wish_id, user=request.user)
        wishlist.delete()
        return Response({"message": "삭제 완료"}, status=status.HTTP_200_OK)


class WishlistToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, wish_id):
        wishlist = get_object_or_404(Wishlist, id=wish_id, user=request.user)
        wishlist.is_active = not wishlist.is_active
        wishlist.save()
        return Response(
            {"message": "상태가 변경되었습니다."}, status=status.HTTP_200_OK
        )
