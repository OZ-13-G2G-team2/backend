from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer



class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 접근 가능

# 유저 정보 조회 API
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # 로그인 필요
    lookup_field = 'id'