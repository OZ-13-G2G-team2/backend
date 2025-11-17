import logging
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from django.db import transaction
from app.user_auth.serializers import (
    UserRegisterSerializer,
    SellerRegisterSerializer,
    LogoutSerializer,
    CustomTokenObtainPairSerializer,
)
from app.user_auth.utils import send_activation_email, EMAIL_SIGNER, MAX_AGE_SECONDS

User = get_user_model()
logger = logging.getLogger("app")


# 이메일 인증 메일 전송
@extend_schema(tags=["이메일 전송"])
class EmailSendView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")

        if not email:
            logger.warning("이메일 인증 요청 실패 - email 필드 누락")
            return Response(
                {"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"이메일 인증 실패 - 존재하지 않는 이메일: {email}")
            return Response(
                {"error": "해당 이메일의 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.is_active:
            logger.warning(f"이메일 인증 요청 실패 - 이미 활성화된 계정: {user.email}")
            return Response(
                {"error": "이미 이메일 인증이 완료된 계정입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            send_activation_email(user)
            logger.info(
                f"[이메일 인증 발송 완료] email={user.email}, user_id={user.id}"
            )
        except Exception as e:
            logger.error(f"[이메일 인증 발송 실패] email={email}, error={e}")
            return Response(
                {"error": "이메일 발송에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "인증 메일이 발송되었습니다."}, status=status.HTTP_200_OK
        )

    @transaction.atomic  # DB 업데이트
    def get(self, request):
        token = request.query_params.get("token")
        logger.info(f"[이메일 인증 링크 GET 요청] token={token}")

        if not token:
            logger.warning("이메일 인증 실패 - token 없음")
            return Response(
                {"error": "token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        redirect_url_base = f"{settings.FRONTEND_URL}/email/certification"
        user_pk_str = None

        try:
            user_pk_str = EMAIL_SIGNER.unsign(token, max_age=MAX_AGE_SECONDS)

        except SignatureExpired:
            logger.warning("이메일 인증 실패 - 토큰 만료")
            return redirect(f"{redirect_url_base}?status=expired")

        except BadSignature:
            logger.warning(f"이메일 인증 실패 - 잘못된 token/서명: {token}")
            return redirect(f"{redirect_url_base}?status=invalid")

        if not user_pk_str:
            logger.error(
                f"이메일 인증 실패 - Signer 복원 실패, 복원된 값: {user_pk_str}"
            )
            return redirect(f"{redirect_url_base}?status=invalid")

        try:
            user_pk = int(user_pk_str)

        except (TypeError, ValueError):
            # unsign() 결과가 유효하지 않은 경우 (None 또는 숫자가 아닌 문자열)
            logger.error(
                f"이메일 인증 실패 - 복원된 PK '{user_pk_str}'가 정수형이 아님."
            )
            return redirect(f"{redirect_url_base}?status=invalid")

        except ValueError:
            logger.warning(f"이메일 인증 실패 - 유효하지 않은 PK 형식: {user_pk}")
            return redirect(f"{redirect_url_base}?status=invalid")

        try:
            # 복원된 pk로 사용자 조회
            user = User.objects.get(pk=user_pk)

        except (TypeError, ValueError):
            logger.error(
                f"이메일 인증 실패 - 복원된 PK '{user_pk_str}'가 정수형이 아님."
            )
            return redirect(f"{redirect_url_base}?status=invalid")

        # 이미 활성화된 계정인 경우
        try:
            # 복원된 pk로 사용자 조회
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            logger.warning(f"이메일 인증 실패 - 존재하지 않는 유저 PK: {user_pk}")

        # 인증 완료 처리
        user.is_active = True
        user.save()

        logger.info(f"[이메일 인증 성공] user={user.email}")

        redirect_url = f"{redirect_url_base}/{user.email}?status=success"
        return redirect(redirect_url)


# 일반 회원가입
@extend_schema(tags=["유저 회원가입"])
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def perform_create(self, serializer):
        logger.info("[일반 회원가입 요청]")
        user = serializer.save()
        logger.info(f"[일반 회원가입 성공] email={user.email}")
        return user


# 판매자 회원가입
@extend_schema(tags=["판매자 회원가입"])
class SellerRegisterView(generics.CreateAPIView):
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def perform_create(self, serializer):
        logger.info("[판매자 회원가입 요청]")
        user = serializer.save()
        logger.info(f"[판매자 회원가입 성공] email={user.email}")
        return user


# 로그인
@extend_schema(tags=["유저 로그인"], summary="로그인")
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request):
        logger.info(f"[로그인 시도] email={request.data.get('email')}")

        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.info(f"[로그인 성공] email={request.data.get('email')}")
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# 로그아웃
@extend_schema(tags=["유저 로그인"], summary="로그 아웃", request=LogoutSerializer)
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        logger.info(f"[로그아웃 요청] user={request.user.email}")

        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"[로그아웃 성공] user={request.user.email}")
            return Response(
                {"detail": "로그아웃 되었습니다."}, status=status.HTTP_205_RESET_CONTENT
            )

        except Exception as e:
            logger.warning(f"[로그아웃 실패] user={request.user.email}, error={str(e)}")
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 토큰 갱신
@extend_schema(tags=["토큰 갱신"])
class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("[토큰 갱신 요청]")
        return super().post(request, *args, **kwargs)
