from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "market_db"),
        "USER": os.getenv("POSTGRES_USER", "marketadmin"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "passwordasd1"),
        "HOST": os.getenv("DB_HOST", "localhost"),  # docker-compose의 서비스명
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

# 실제 우리 서비스의 도메인을 넣으면 된다.
# CSRF_TRUSTED_ORIGINS = [
#     "https://우리 도메인",
# ]