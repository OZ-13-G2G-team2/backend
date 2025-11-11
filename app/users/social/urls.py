
from django.urls import path
from .views import GoogleLoginView, KakaoLoginView, NaverLoginView

urlpatterns = [
    # API 요청을 받는 엔드포인트
    path("google/", GoogleLoginView.as_view(), name="google_login"),
    path("kakao/", KakaoLoginView.as_view(), name="kakao_login"),
    path("naver/", NaverLoginView.as_view(), name="naver_login"),
]