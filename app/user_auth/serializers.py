import logging
import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from app.sellers.models import Seller
from app.users.serializers import validate_strong_password
from app.user_auth.utils import send_activation_email
from django.db import transaction


logger = logging.getLogger("app")


User = get_user_model()


# 회원가입 공동 로직
class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "address",
            "phone_number",
            "password",
            "password2",
        ]

    def validate(self, data):
        # 비밀번호 일치 확인
        if data["password"] != data["password2"]:
            logger.warning(
                f"회원가입 실패 - 비밀번호 불일치: email={data.get('email')}"
            )
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )

        # 이메일 중복 확인
        if User.objects.filter(email=data["email"]).exists():
            logger.warning(f"회원가입 실패 - 이메일 중복: {data['email']}")
            raise serializers.ValidationError({"email": "이미 사용 중인 이메일입니다."})

        # 전화번호 중복 확인
        phone_number = data.get("phone_number")
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            logger.warning(f"회원가입 실패 - 전화번호 중복: {phone_number}")
            raise serializers.ValidationError(
                {"phone_number": "이미 사용 중인 전화번호입니다."}
            )

        # 비밀번호 복잡도 검증
        validate_strong_password(data["password"])

        return data

    def create_user(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        try:
            send_activation_email(user)
            logger.info(f"회원가입 성공 & 이메일 발송 완료: {user.email}")
        except Exception as e:
            logger.error(f"이메일 발송 실패 - email: {user.email}, error={str(e)}")

        return user


# 유저 회원가입 시리얼라이저
class UserRegisterSerializer(BaseRegisterSerializer):
    @transaction.atomic
    def create(self, validated_data):
        user = self.create_user(validated_data)
        logger.info(f"일반 회원가입 성공: {user.email}")
        return user


# 판매자 회원가입
class SellerRegisterSerializer(BaseRegisterSerializer):
    business_address = serializers.CharField(write_only=True)
    business_name = serializers.CharField(write_only=True)
    business_number = serializers.CharField(write_only=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            "business_address",
            "business_name",
            "business_number",
        ]

    def validate_business_number(self, value):
        if len(value) != 10:
            logger.warning(f"판매자 회원가입 실패 - 사업자번호 길이 오류: {value}")
            raise serializers.ValidationError("사업자등록번호는 10자리여야 합니다.")

        if not re.match(r"^\d{10}$", value):
            logger.warning(f"판매자 회원가입 실패 - 사업자번호 숫자 아님: {value}")
            raise serializers.ValidationError(
                "사업자등록번호는 숫자만 포함해야 합니다."
            )
        return value

    def validate(self, data):
        data = super().validate(data)
        if Seller.objects.filter(business_number=data["business_number"]).exists():
            logger.warning(
                f"판매자 회원가입 실패 - 사업자번호 중복: {data['business_number']}"
            )
            raise serializers.ValidationError(
                {"business_number": "이미 등록된 사업자번호입니다."}
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        business_address = validated_data.pop("business_address")
        business_name = validated_data.pop("business_name")
        business_number = validated_data.pop("business_number")

        # 공통 유저 생성 로직 재사용
        user = self.create_user(validated_data)

        # 판매자 생성
        Seller.objects.create(
            user=user,
            business_address=business_address,
            business_name=business_name,
            business_number=business_number,
        )

        logger.info(
            f"판매자 회원가입 성공: email={user.email}, 사업자번호={business_number}"
        )
        return user


# 로그인 토큰 발급 내용 개선 시리얼라이저
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # user 일때
        token["username"] = user.username

        if Seller.objects.filter(user=user).exists():
            token["is_seller"] = True
        return token

    def validate(self, attrs):
        # 이메일과 비밀번호를 확인
        email = attrs.get("email")
        password = attrs.get("password")
        if not email and not password:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")
        if not email:
            raise serializers.ValidationError("이메일 확인해주세요.")
        if not password:
            raise serializers.ValidationError("비밀번호를 확인해주세요.")

        # 사용자 존재 확인
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("이메일 또는 비밀번호가 올바르지 않습니다.")

        # 비밀번호 확인
        if not user.check_password(password):
            raise AuthenticationFailed("비밀번호가 올바르지 않습니다.")

        # 이메일 미인증(비활성) 체크
        if not user.is_active:
            raise AuthenticationFailed(
                {
                    "error": "이메일 인증이 필요합니다.",
                    "resend": True,  # 프론트에서 '재전송 버튼' 표시
                    "email": email,  # 다시 입력할 필요 없이 그대로 사용 가능
                }
            )
        # 로그인 성공
        logger.info(f"로그인 성공: {email}")

        # 토큰 생성
        self.user = user
        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return data


# 로그아웃 시리얼라이저
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        logger.info("로그아웃 시도 - refresh token 전달됨")
        return attrs
