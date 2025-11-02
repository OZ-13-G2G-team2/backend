from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


# 유저 정보 조회 API
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    #
    # def get(self, request, *args, **kwargs):
    #     try:
    #         user = self.get_object()
    #         serializer = self.get_serializer(user)
    #         return Response(serializer.data)
    #     except User.DoesNotExist:
    #         return Response(
    #             {"detail":"해당 유저를 찾을 수 없습니다."},
    #             status=status.HTTP_404_NOT_FOUND
    #         )
