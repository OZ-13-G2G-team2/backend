import re

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from app.sellers.models import Seller
from .utils import send_activation_email
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "address",
            "phone_number",
            "created_at",
            "updated_at",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
            "is_staff",
            "is_superuser",
        )
# 비밀번호 복잡도 인증 8자 이상, 영어, 숫자, 특수 문자
def validate_strong_password(value):
    if len(value) < 8:
        raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not re.search(r"[A-Za-z]", value):
        raise serializers.ValidationError("비밀번호에 영문이 포함되어야 합니다.")
    if not re.search(r"\d", value):
        raise serializers.ValidationError("비밀번호에 숫자가 포함되어야 합니다.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise serializers.ValidationError("비밀번호에 특수문자가 포함되어야 합니다.")
    return value

#회원가입 공동 로직
class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "address", "phone_number", "password", "password2"]

    def validate(self, data):
        # 비밀번호 일치 확인
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})

        # 이메일 중복 확인
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "이미 사용 중인 이메일입니다."})

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
        except Exception as e:
            # 이메일 발송 실패 시에도 유저는 생성되도록
            print(f"Email sending failed: {e}")
        return user


# 유저 회원가입 시리얼라이저
class UserRegisterSerializer(BaseRegisterSerializer):
    @transaction.atomic
    def create(self, validated_data):
        return self.create_user(validated_data)


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


    def validate(self, data):
        data = super().validate(data)
        if Seller.objects.filter(business_number=data["business_number"]).exists():
            raise serializers.ValidationError({"business_number": "이미 등록된 사업자번호입니다."})
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

        return user


# 비밀번호 변경
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    # 기존 비밀 번호와 비교하여 valid 확인
    def validate(self, data):
        user = self.context["request"].user

        # 기존 비밀번호 일치 확인
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "기존 비밀번호가 올바르지 않습니다."})

        # 새 비밀번호 복잡도 검사
        validate_strong_password(data["new_password"])

        # Django 전역 비밀번호 정책 검사
        validate_password(data["new_password"], user=user)

        return data