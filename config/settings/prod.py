import os  # noqa
from pathlib import Path  # noqa
from .base import *  # noqa: F403
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / "/home/ec2-user/app/.env")  # noqa: F405
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
ALLOWED_HOSTS = ["backend-g2g.p-e.kr', 'www.backend-g2g.p-e.kr"]

# CORS 관련
CSRF_TRUSTED_ORIGINS = [
    "http://13.124.51.27:8000",
    "http://13.124.51.27",
]

# axios 등에서 credentials(쿠키) 포함 요청을 할 경우
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),  # docker-compose의 서비스명
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

STATIC_URL = '/static/'  # noqa: F405
STATIC_ROOT = '/home/ec2-user/app/static' # noqa: F405
MEDIA_URL = '/media/'  # noqa: F405
MEDIA_ROOT = '/home/ec2-user/app/media'  # noqa: F405

# build_absolute_uri 문제 방지 (중요)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True          # HTTP -> HTTPS 리다이렉트
SESSION_COOKIE_SECURE = True        # 세션 쿠키 HTTPS 전용
CSRF_COOKIE_SECURE = True           # CSRF 쿠키 HTTPS 전용