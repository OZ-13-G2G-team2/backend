from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserTokenRefreshView,
    UserDetailView,
    SellerRegisterView,
    ChangePasswordView,
    UserList,
    UserActivateView,
    ResendActivationEmailView,
)

app_name = "users"

urlpatterns = [
    # --- 관리/조회 ---
    path("list/", UserList.as_view(), name="user-list"),# 전체 유저 조회
    # --- 인증 ---
    path("activate/<uidb64>/<token>/", UserActivateView.as_view(), name="user-activate"),
    path("activate/resend/", ResendActivationEmailView.as_view(), name="resend-activation"), #이메일 재전송
    # --- 회원가입 ---
    path("signup/", UserRegisterView.as_view(), name="user-signup"),  # 일반 유저
    path("signup/seller/", SellerRegisterView.as_view(), name="seller-signup"),  # 판매자

    # --- 로그인 / 토큰 ---
    path("login/", UserLoginView.as_view(), name="login"),  # JWT 발급
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token-refresh"),

    # --- 유저 정보 ---
    path("<int:id>/", UserDetailView.as_view(), name="user-detail"),  # 상세 조회
    path("password/change/", ChangePasswordView.as_view(), name="change-password"),
]
