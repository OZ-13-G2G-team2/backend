from django.urls import path
from .views import UserRegisterView, UserLoginView, UserTokenRefreshView, UserDetailView, SellerRegisterView

app_name = "users"

urlpatterns = [
    # user/seller 회원가입
    path('signup/', UserRegisterView.as_view(), name='user-signup'),
    path('signup/seller', SellerRegisterView.as_view(), name='seller-signup'),
    # 유저 로그인/ 로그아웃
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    # todo 로그아웃 구현
    path('token/refresh/', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
]
