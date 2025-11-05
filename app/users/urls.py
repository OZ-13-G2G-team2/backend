from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserTokenRefreshView,
    UserDetailView,
    SellerRegisterView,
    ChangePasswordView,
    UserList, PreSignUpView, UserActivateView,
)

app_name = "users"

urlpatterns = [
    # 전체 유정 조회
    path("a_users/", UserList.as_view(), name="user-list"),
    #이메일 인증
    path("pre-signup/", PreSignUpView.as_view(), name="pre-signup"),
    path("activate/", UserActivateView.as_view(), name="user-activate"),
    # user/seller 회원가입
    path("signup/", UserRegisterView.as_view(), name="user-signup"),
    path("signup/seller/", SellerRegisterView.as_view(), name="seller-signup"),
    # 유저 로그인/ 로그아웃
    path("login/", UserLoginView.as_view(), name="token_obtain_pair"),
    # todo 로그아웃 구현
    # 유저정보 조회
    path("<int:id>/", UserDetailView.as_view(), name="user-detail"),
    path("password/", ChangePasswordView.as_view(), name="change-password"),
    # 토큰 발급
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
]
