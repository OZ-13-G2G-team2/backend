from django.urls import path
from .views import (
    UserActivateView,
    CheckUserActiveView,
    ResendActivationEmailView,
    UserRegisterView,
    SellerRegisterView,
    UserTokenRefreshView,
    UserLoginView,
    UserLogoutView,
)

app_name = "user_auth"

urlpatterns = [
    # --- 인증 ---
    path("activate/", UserActivateView.as_view(), name="user-activate"),
    path(
        "is_active/", CheckUserActiveView.as_view(), name="is_active"
    ),  # 유저가 is_active인지 확인 해줌
    path(
        "email-send/",
        ResendActivationEmailView.as_view(),
        name="email-send",
    ),  # 이메일 재전송
    # --- 회원가입 ---
    path("signup/", UserRegisterView.as_view(), name="user-signup"),  # 일반 유저
    path(
        "signup-seller/", SellerRegisterView.as_view(), name="seller-signup"
    ),  # 판매자
    # --- 로그인 / 토큰 ---
    path("login/", UserLoginView.as_view(), name="login"),  # JWT 발급
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
