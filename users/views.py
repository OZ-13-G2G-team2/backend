from django.contrib.auth import update_session_auth_hash
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
)


# 유저 전체 조회
class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

#user/signup
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


# seller/signup
class SellerRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.AllowAny]


# 로그인 (JWT 발급)
class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


# 토큰 갱신
class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


# 유저 정보 조회 API
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    #
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

class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated] # 로그인 유저만 할 수 있음.

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

            return Response({"detail": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)