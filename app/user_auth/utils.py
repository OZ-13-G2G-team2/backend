from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.signing import TimestampSigner
import logging

logger = logging.getLogger("app")

# signer 객체 정의 토큰 유효 시간 설정
EMAIL_SIGNER = TimestampSigner(salt="email-activation", key=settings.SECRET_KEY)
MAX_AGE_SECONDS = 3600  # 1시간 (60 * 60)


def send_activation_email(user):

    token = EMAIL_SIGNER.sign(str(user.pk))

    activation_link = f"{settings.BACKEND_URL}/api/auth/email-send/?token={token}"

    subject = "회원가입 이메일 인증"
    text_content = f"안녕하세요 {user.username}님,\n아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n{activation_link}"
    html_content = f"""
    <html>
    <body>
        <p>안녕하세요 <strong>{user.username}</strong>님,</p>
        <p>아래 버튼을 클릭하여 이메일 인증을 완료해주세요:</p>
        <a href="{activation_link}"
           style="display:inline-block;padding:12px 24px;
                  background-color:#4CAF50;color:white;
                  text-decoration:none;border-razdius:4px;">
            이메일 인증하기
        </a>
        <p>또는 아래 링크를 복사해 브라우저에 붙여넣으세요:</p>
        <p><a href="{activation_link}">{activation_link}</a></p>
    </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"[utils] 이메일 발송 성공: {user.email}")
    except Exception as e:
        logger.error(f"[utils] Email sending failed: {e}, user={user.email}")
        raise

    return activation_link
