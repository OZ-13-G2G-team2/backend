from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    SellerRegisterSerializer,
    ChangePasswordSerializer,
    PreSignUpSerializer,
)
from drf_spectacular.utils import extend_schema

from .utils import send_activation_email


# 유저 전체 조회
@extend_schema(tags=["유저 전체 조회"])
class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# 이메일 인증 요청 api
@extend_schema(tags=["이메일 인증"], summary="이메일 인증용 임시 유저")
class PreSignUpView(generics.CreateAPIView):
    serializer_class = PreSignUpSerializer
    permission_classes = [permissions.AllowAny]


# 이메일 인증
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


# user/signup
@extend_schema(tags=["유저 회원가입"])
class UserRegisterView(generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"
    # 회원 가입시 유저정보에서 is_active를 False로 설정 한뒤 email로 활성화에 필요한 이메일을 전송


# seller/signup
@extend_schema(tags=["판매자 회원가입"])
class SellerRegisterView(generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"


# 로그인 (JWT 발급)
@extend_schema(tags=["유저 로그인"])
class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


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
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user

            # 기존 비밀번호와 일치한지 확인
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response(
                    {"detail": "현재 비밀번호가 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 새로운 비밀번호 설정
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()

            # 비밀번호 변경 후에도 로그인 유지
            update_session_auth_hash(request, user)

            return Response(
                {"detail": "회원 비밀 번호 수정."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
