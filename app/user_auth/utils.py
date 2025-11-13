import uuid

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives


def send_activation_email(user):
    user.email_token = str(uuid.uuid4())
    user.save()

    activation_link = f"{settings.BACKEND_URL}/api/auth/email-send/?token={user.email_token}"

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
    except Exception as e:
        print(f"Email sending failed: {e}")

    return activation_link
