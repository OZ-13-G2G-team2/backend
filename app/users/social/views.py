
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# 프론트엔드 URL은 settings.py에서 가져와 사용하거나, 아래와 같이 임시로 지정할 수 있습니다.
# 실제 운영 환경에서는 settings.py의 환경 변수를 사용해야 합니다.
FRONTEND_URL = "http://localhost:3000"

# --- Naver 로그인 뷰 ---
class NaverLoginView(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    # 네이버 개발자 센터에 등록된 리다이렉트 URI와 일치해야 합니다.
    callback_url = f"{FRONTEND_URL}/social/naver/callback"
    client_class = OAuth2Client

# --- Google 로그인 뷰 ---
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # Google Developer Console에 등록된 리다이렉트 URI와 일치해야 합니다.
    callback_url = f"{FRONTEND_URL}/social/google/callback"
    client_class = OAuth2Client

# --- Kakao 로그인 뷰 ---
class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    # 카카오 개발자 센터에 등록된 리다이렉트 URI와 일치해야 합니다.
    # dj-rest-auth는 이 URL로 Authorization Code를 받습니다.
    callback_url = f"{FRONTEND_URL}/social/kakao/callback"
    client_class = OAuth2Client

