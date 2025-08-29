import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env in project root
load_dotenv(BASE_DIR / ".env")

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").strip().lower() in {"1", "true", "yes", "on"}

# Hosts
_raw_hosts = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS = _raw_hosts if _raw_hosts else (["*"] if DEBUG else [])
INTERNAL_IPS = ["127.0.0.1"]
APPEND_SLASH = True

CORS_ALLOWED_ORIGINS = [
    # os.getenv("WEB_URL"),
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "debug_toolbar",
    "rest_framework",
    "drf_spectacular",
    # Local apps
    "assets",
    "django_extensions",
    "django_filters",
    # Mozilla OIDC
    "mozilla_django_oidc",
    # CORS
    "corsheaders",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "devassets_manager.middleware.DetailedLoggingMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "devassets_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "devassets_manager.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF & API schema
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "assets.auth.cookie_jwt_auth.CookieJWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": "5",
    "EXCEPTION_HANDLER": "devassets_manager.utils.custom_exception_handler",
}


SPECTACULAR_SETTINGS = {
    "TITLE": "devassets_manager API",
    "DESCRIPTION": "API schema",
    "VERSION": "1.0.0",
}

# CELERY SETTINGS
CELERY_BROKER_URL = "redis://redis:6379/0"

# EMAIL SETTINGS
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# REDIS SETTINGS
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

# JWT SETTINGS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # "AUTH_HEADER_TYPES": ("Bearer",),
}

# DJANGO-REDIS SETTINGS
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# LOGGING SETTINGS

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "devassets_manager/logs/project.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": True,
        },
        "devassets_manager": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "assets": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "mozilla_django_oidc": {"handlers": ["console"], "level": "DEBUG"},
    },
}


# CUSTOM AUTHENTICATION BACKEND
AUTHENTICATION_BACKENDS = [
    "assets.auth.google_oidc_backend.GoogleOIDCBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# GOOGLE OIDC CREDENTIAL
OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET")


# INFO FROM GOOGLE
OIDC_RP_SCOPES = "openid email profile"
OIDC_RP_SIGN_ALGO = "RS256"

# GOOGLE ENDPOINTS
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
OIDC_OP_JWKS_ENDPOINT = "https://www.googleapis.com/oauth2/v3/certs"
OIDC_OP_USER_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
OIDC_CALLBACK_CLASS = (
    "assets.auth.custom_oidc_callback.CustomOIDCAuthenticationCallbackView"
)


# LOGIN, LOGOUT FLOW
LOGIN_URL = "/oidc/authenticate/"
# LOGIN_REDIRECT_URL = "http://127.0.0.1:5173/dashboard/"
LOGOUT_REDIRECT_URL = "http://127.0.0.1:5173/login/"


ALLOW_LOGOUT_GET_METHOD = True
OIDC_CREATE_USER = True
OIDC_AUTH_REQUEST_EXTRA_PARAMS = {"prompt": "select_account"}
