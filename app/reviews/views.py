from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Review
from .serializers import ReviewSerializer, ReviewImageSerializer
from drf_spectacular.utils import extend_schema


# 리뷰 등록
@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 관리 ",
    description="상품에 대한 리뷰 기능",
)
class ReviewCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 상품별 리뷰 조회
@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 조회 ",
    description="상품에 대한 리뷰 조회 기능",
)
class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id")
        return Review.objects.filter(product_id=product_id)


@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 수정 ",
    description="상품에 대한 리뷰 수정 기능",
)
# 리뷰 수정
@extend_schema(tags=["리뷰 수정"])
class ReviewUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 삭제 ",
    description="상품에 대한 리뷰 삭제기능",
)
# 리뷰 삭제
@extend_schema(tags=["리뷰 삭제"])
class ReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 좋아요 ",
    description="상품에 대한 리뷰 좋아요 기능",
)
# 리뷰 좋아요 추가
@extend_schema(tags=["리뷰 좋아요"])
class ReviewLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return Response({"error": "리뷰를 찾을 수 없습니다."}, status=404)

        review.like_count += 1
        review.save()
        return Response({"message": "좋아요 +1"}, status=200)


@extend_schema(
    tags=["리뷰 관리"],
    summary="리뷰 상품이미지 ",
    description="상품에 대한 이미지 리뷰 기능",
)
# 리뷰 사진 업로드
@extend_schema(tags=["리뷰 사진"])
class ReviewImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return Response({"error": "리뷰 없음"}, status=404)

        image_url = request.data.get("image_url")
        if not image_url:
            return Response({"error": "이미지 누락"}, status=400)

        review.image_url = image_url
        review.save()
        return Response({"message": "리뷰 사진이 등록되었습니다."}, status=200)
