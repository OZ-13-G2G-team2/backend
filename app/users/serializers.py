import logging
import re

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

logger = logging.getLogger(__name__)


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
    try:
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError("비밀번호에 영문이 포함되어야 합니다.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("비밀번호에 숫자가 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "비밀번호에 특수문자가 포함되어야 합니다."
            )
    except Exception as e:
        logger.warning(f"[비밀번호 정책 실패] error={e}")
        raise e

    return value


# 비밀번호 변경
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["old_password"]):
            logger.warning(
                f"[비밀번호 변경 실패 - 기존 비밀번호 불일치] user={user.email}"
            )
            raise serializers.ValidationError(
                {"old_password": "기존 비밀번호가 올바르지 않습니다."}
            )

        validate_strong_password(data["new_password"])
        validate_password(data["new_password"], user=user)

        logger.info(f"[비밀번호 변경 검증 통과] user={user.email}")
        return data
