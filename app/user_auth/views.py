
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from django.db import transaction
from app.user_auth.serializers import (
    UserRegisterSerializer,
    SellerRegisterSerializer,
    LogoutSerializer,
)
from app.user_auth.utils import send_activation_email

User = get_user_model()

@extend_schema(tags=["이메일 전송"])
class EmailSendView(APIView):
    permission_classes = [permissions.AllowAny]

    # 이메일 발송
    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.select_for_update().get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "해당 이메일의 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        link = send_activation_email(user)
        print("Activation link:", link)

        return Response(
            {"message": "인증 메일이 발송되었습니다."}, status=status.HTTP_200_OK
        )

    # 활성화 및 프론트 리디렉션
    def get(self, request):
        token = request.query_params.get("token")

        # token 없을 때
        if not token:
            return Response(
                {"error": "token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # token으로 유저 조회
        try:
            user = User.objects.get(email_token=token)
        except User.DoesNotExist:
            redirect_url = f"{settings.FRONTEND_URL}/email/certification?status=invalid"
            return redirect(redirect_url)

        # 인증 완료 처리
        user.is_active = True
        user.email_token = None  # 토큰 1회성
        user.save()

        # 프론트엔드로 리다이렉트
        redirect_url = (
            f"{settings.FRONTEND_URL}/email/certification/{user.email}?status=success"
        )
        return redirect(redirect_url)


# user/signup
@extend_schema(tags=["유저 회원가입"])
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()


# seller/signup
@extend_schema(tags=["판매자 회원가입"])
class SellerRegisterView(generics.CreateAPIView):
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()


# 로그인 (JWT 발급)
@extend_schema(tags=["유저 로그인"], summary="로그인")
class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


# 로그 아웃
@extend_schema(tags=["유저 로그인"], summary="로그 아웃", request=LogoutSerializer)
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "로그아웃 되었습니다."}, status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:
            # refresh 토큰이 유효하지 않은 토큰일 때
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 토큰 갱신 todo 토큰갱신 테스트 해보기
@extend_schema(tags=["토큰 갱신"])
class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
