from .base import * # noqa: F403

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        "NAME": os.getenv("CI_DB_NAME", "ci_db"),  # noqa: F405
        "USER": os.getenv("CI_DB_USER", "ci_user"),
        "PASSWORD": os.getenv("CI_DB_PASSWORD", "ci_pass"),
        "HOST": os.getenv("CI_DB_HOST", "db"), # docker-compose 서비스명
        "PORT": os.getenv("CI_DB_PORT", "5432"),
    }
}

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
