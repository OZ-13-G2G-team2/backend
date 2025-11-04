from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from sellers.models import Seller
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
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
            "is_staff",
        )

# email 인증시 임시 회원 생성 시리얼라이저
class PreSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("이미 사용중인 이메일입니다.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"is_active": False}
        )

        send_activation_email(user)
        return user

# 유저 회원가입 시리얼라이저
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)  # 비밀번호 확인

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

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.set_password(password)
        instance.save()
        return instance

        user = User.objects.create_user(**validated_data)
        return user


# 판매자 회원가입
class SellerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    business_address = serializers.CharField(write_only=True)
    business_name = serializers.CharField(write_only=True)
    business_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "username",
            "address",
            "phone_number",
            "business_address",
            "business_name",
            "business_number",
        ]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"message": "비밀번호가 일치하지 않습니다."}
            )
        return data
    @transaction.atomic
    def create(self, validated_data):
        business_address = validated_data.pop("business_address")
        business_name = validated_data.pop("business_name")
        business_number = validated_data.pop("business_number")
        validated_data.pop("password2")

        user = User.objects.create_user(**validated_data)
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
