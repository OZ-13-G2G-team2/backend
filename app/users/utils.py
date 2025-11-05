from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail


def send_activation_email(user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    activation_link = f"{settings.FRONTEND_URL}/activate/{uidb64}/{token}"

    send_mail(
        subject="이메일 인증 요청",
        message=f"아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n\n{activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
