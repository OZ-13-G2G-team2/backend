from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, SellerRegisterSerializer


#user/signup
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

# seller/signup
class SellerRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.AllowAny]

# 로그인 (JWT 발급)
class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

# 토큰 갱신
class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


# 유저 정보 조회 API
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'