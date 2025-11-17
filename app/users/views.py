import logging
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ChangePasswordSerializer
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)
User = get_user_model()


# 유저 전체 조회
@extend_schema(tags=["유저 전체 조회"])
class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        logger.info(f"[유저 전체 조회] 관리자={request.user.email}")
        return super().list(request, *args, **kwargs)


# 유저 상세 조회/수정/삭제
@extend_schema(tags=["유저 상세"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user = super().get_object()
        if self.request.user != user:
            logger.warning(
                f"[유저 정보 접근 차단] 요청자={self.request.user.email}, 대상 유저 id={user.id}"
            )
            raise PermissionDenied("본인 계정만 접근할 수 있습니다.")

        logger.info(f"[유저 상세 조회] user={user.email}")
        return user

    def update(self, request, *args, **kwargs):
        logger.info(f"[유저 정보 수정] user={request.user.email}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.warning(f"[유저 삭제] user={request.user.email}")
        return super().destroy(request, *args, **kwargs)


# 비밀번호 변경
@extend_schema(tags=["비밀번호 변경"])
class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"[비밀번호 변경 요청] user={request.user.email}")

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            user = request.user

            # 기존 비밀번호 확인
            if not user.check_password(serializer.validated_data.get("old_password")):
                logger.warning(
                    f"[비밀번호 변경 실패 - 기존 비밀번호 불일치] user={user.email}"
                )
                return Response(
                    {"detail": "현재 비밀번호가 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 변경 처리
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            update_session_auth_hash(request, user)

            logger.info(f"[비밀번호 변경 성공] user={user.email}")

            return Response(
                {"detail": "회원 비밀 번호 수정."}, status=status.HTTP_200_OK
            )
