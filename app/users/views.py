from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    ChangePasswordSerializer,
)
from drf_spectacular.utils import extend_schema


User = get_user_model()


# 유저 전체 조회
@extend_schema(tags=["유저 전체 조회"])
class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


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
