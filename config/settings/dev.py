from .base import * # noqa: F403

DEBUG = True

load_dotenv(BASE_DIR / '.env')
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        "NAME": BASE_DIR / "db.sqlite3", # noqa: F405
    }
}

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]