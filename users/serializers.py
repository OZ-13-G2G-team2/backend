from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'address', 'phone_number', 'created_at', 'updated_at',  'is_active', 'is_admin', 'is_staff')
        read_only_fields = ('id', 'created_at', 'updated_at',  'is_active', 'is_admin', 'is_staff')

    class UserRegisterSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
        password2 = serializers.CharField(write_only=True, required=True)  # 비밀번호 확인용

        class Meta:
            model = User
            fields = ['email', 'username', 'address', 'phone_number', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user