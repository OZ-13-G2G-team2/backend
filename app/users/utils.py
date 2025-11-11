from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives


def send_activation_email(user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    activation_link = f"{settings.FRONTEND_URL}/api/users/activate/{uidb64}/{token}/"

    subject = "회원가입 이메일 인증"

    # 텍스트 버전
    text_content = f"""
안녕하세요 {user.username}님,

아래 링크를 클릭하여 이메일 인증을 완료해주세요:

{activation_link}

감사합니다.
    """

    # HTML 버전 (클릭 가능한 링크)
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>안녕하세요 <strong>{user.username}</strong>님,</p>
        <p>아래 버튼을 클릭하여 이메일 인증을 완료해주세요:</p>
        <p>
            <a href="{activation_link}" 
               style="display: inline-block; padding: 12px 24px; 
                      background-color: #4CAF50; color: white; 
                      text-decoration: none; border-radius: 4px;">
                이메일 인증하기
            </a>
        </p>
        <p>또는 아래 링크를 복사하여 브라우저에 붙여넣으세요:</p>
        <p><a href="{activation_link}">{activation_link}</a></p>
        <p>감사합니다.</p>
    </body>
    </html>
    """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        # HTML 이메일 발송
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"✅ 이메일 발송 성공: {user.email}")
    except Exception as e:
        # 실패해도 회원가입은 유지, 로그 남김
        print(f"❌ 이메일 발송 실패: {e}")