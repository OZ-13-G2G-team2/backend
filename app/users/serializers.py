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
#회원가입 공동 로직
class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "address", "phone_number", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "이미 사용 중인 이메일입니다."})
        return data

    def create_user(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        send_activation_email(user)
        return user


# 유저 회원가입 시리얼라이저
class UserRegisterSerializer(BaseRegisterSerializer):
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
    new_password = serializers.CharField(required=True, validators=[validate_password])
