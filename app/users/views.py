from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    SellerRegisterSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
)
from drf_spectacular.utils import extend_schema

from .utils import send_activation_email


# 유저 전체 조회
@extend_schema(tags=["유저 전체 조회"])
class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# 이메일 인증 링크 발송
@extend_schema(tags=["이메일 인증"], summary="이메일 인증후 활성화")
class UserActivateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "유효하지 않은 링크입니다."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "이메일 인증이 완료되었습니다."}, status=200)

        return Response({"error": "토큰이 유효하지 않습니다."}, status=400)


# 이메일 인증 재전송
@extend_schema(tags=["이메일 인증"], summary="이메일 인증 재전송")
class ResendActivationEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "해당 이메일의 사용자가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_active:
            return Response(
                {"message": "이미 인증이 완료된 계정입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이메일 재전송
        send_activation_email(user)
        return Response(
            {"message": "인증 메일을 다시 발송했습니다."}, status=status.HTTP_200_OK
        )


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


# 유저 정보 조회 API
@extend_schema(tags=["유저 상세"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user = super().get_object()
        if self.request.user != user:
            raise PermissionDenied("본인 계정만 접근할 수 있습니다.")
        return user

    # def get(self, request, *args, **kwargs):
    #     try:
    #         user = self.get_object()
    #         serializer = self.get_serializer(user)
    #         return Response(serializer.data)
    #     except User.DoesNotExist:
    #         return Response(
    #             {"detail":"해당 유저를 찾을 수 없습니다."},
    #             status=status.HTTP_404_NOT_FOUND
    #         )


# 비밀번호 변경
@extend_schema(tags=["비밀번호 변경"])
class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]  # 로그인 유저만 할 수 있음.

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            user = request.user

            # 기존 비밀번호와 일치한지 확인
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response(
                    {"detail": "현재 비밀번호가 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # 2. 비밀번호 저장 및 세션 유지 로직
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()

            update_session_auth_hash(request, user)

            return Response(
                {"detail": "회원 비밀 번호 수정."}, status=status.HTTP_200_OK
            )
