from django.http import Http404
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
    serializer_class = WishlistSerializer

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")

        if Wishlist.objects.filter(user=user, product_id=product_id).exists():
            return Response({"error": "이미 존재"}, status=status.HTTP_400_BAD_REQUEST)

        wishlist = Wishlist.objects.create(user=user, product_id=product_id)
        return Response(
            {"message": "위시리스트에 추가되었습니다.", "id": wishlist.id},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        user = request.user
        wishlists = Wishlist.objects.filter(user=user)
        if not wishlists.exists():
            return Response({"error": "위시리스트 없음"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WishlistSerializer(wishlists, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class WishlistDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def delete(self, request, wish_id):
        try:
            wishlist = get_object_or_404(Wishlist, id=wish_id, user=request.user)
        except Http404:
            return Response({"error": "해당 항목 없음"}, status=status.HTTP_404_NOT_FOUND)

        wishlist.delete()
        return Response({"message": "삭제 완료"}, status=status.HTTP_200_OK)


class WishlistToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def patch(self, request, wish_id):
        try:
            wishlist = get_object_or_404(Wishlist, id=wish_id, user=request.user)
        except Http404:
            return Response({"error": "해당 항목 없음"}, status=status.HTTP_404_NOT_FOUND)

        try:
            wishlist.is_active = not wishlist.is_active
            wishlist.save()
        except Exception:
            return Response({"error": "상태 변경 실패"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "상태가 변경되었습니다."}, status=status.HTTP_200_OK)
