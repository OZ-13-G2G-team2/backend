
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # is_active 필드가 False로 설정되어 있다면, 소셜 로그인은 바로 활성화합니다.
        if not user.is_active:
            user.is_active = True

        # 소셜 계정의 Extra Data (raw data)를 가져옵니다.
        data = sociallogin.account.extra_data
        provider = sociallogin.account.provider

        # 이메일은 allauth에서 이미 처리하지만, 추가 필드를 처리합니다.

        # 1. Google
        if provider == 'google':
            # Google은 'name' 필드를 제공할 수 있습니다.
            user.username = data.get('name', user.username)

        # 2. Kakao
        elif provider == 'kakao':
            # 카카오는 'kakao_account' > 'profile' 구조를 가집니다.
            profile = data.get('kakao_account', {}).get('profile', {})
            user.username = profile.get('nickname', user.username)
            # 카카오는 전화번호도 따로 제공할 수 있습니다.
            # user.phone_number = data.get('kakao_account', {}).get('phone_number', user.phone_number)

        # 3. Naver
        elif provider == 'naver':
            # 네이버는 'response' 안에 사용자 정보가 있습니다.
            response = data.get('response', {})
            user.username = response.get('nickname', user.username)
            user.phone_number = response.get('mobile', user.phone_number)

        user.save()
        return user