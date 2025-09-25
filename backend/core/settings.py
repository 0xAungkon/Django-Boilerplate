# Import Libraries
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from loguru import logger
from datetime import timedelta


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load Apps
APPS_DIR = os.path.join(BASE_DIR, "apps")
sys.path.append(APPS_DIR)

# Load Utils
UTILS_DIR = os.path.join(BASE_DIR, "utils")
sys.path.append(UTILS_DIR)

# Load environment variables
load_dotenv()

# Configure logging

# Load Secret Key
if not os.getenv("SECRET_KEY"):
    logger.error("SECRET_KEY environment variable not set")
    exit("")
SECRET_KEY = os.getenv("SECRET_KEY")

# Set Debug Mode
DEBUG = os.getenv("DEBUG") == "True"

# Set Allowed Hosts
ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS").split(",") if os.getenv("ALLOWED_HOSTS") else []
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "common",
    "corsheaders",
    "django_filters",
    "storages",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=99999),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Middleware configurations
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.helpers.Middleware.CsrfExemptMiddleware",  # Custom middleware to disable CSRF check
    "core.helpers.Middleware.HandleErrorsMiddleware",  # Custom middleware to handle Errors
    # 'core.helpers.Middleware.PlatformTokenAuthMiddleware',  # Custom middleware to handle Errors
]

ROOT_URLCONF = "core.urls"


SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
        "X-API-KEY": {"type": "apiKey", "name": "X-API-KEY", "in": "header"},
        # "Platform-API-Token": {
        #     "type": "apiKey",
        #     "name": "Platform-API-Token",
        #     "in": "header",
        # },
    },
    "USE_SESSION_AUTH": False,
    "DEFAULT_GENERATOR_CLASS": "core.schema.CustomSchemaGenerator",  # Use the custom schema generator
}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.helpers.Authentications.PlatformApiTokenAuthentication",  # todo if not default move to viewsets
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        # 'rest_framework.renderers.AdminRenderer',
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",  # Optional for dev
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
}


# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Define the WSGI application
WSGI_APPLICATION = "core.wsgi.application"

# Database configuration
if os.getenv("DATABASE_DRIVER") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DATABASE_NAME"),
            "USER": os.getenv("DATABASE_USER"),
            "PASSWORD": os.getenv("DATABASE_PASSWORD"),
            "HOST": os.getenv("DATABASE_HOST"),
            "PORT": os.getenv("DATABASE_PORT"),
        }
    }
else:
    # Default to SQLite if no DATABASE_URL is provided
    # This is useful for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db/db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]
# If DEBUG is False, add additional password validators
if not DEBUG:
    AUTH_PASSWORD_VALIDATORS += [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]


# Internationalization and Time zone
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE") or "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Media files (User-uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")


# CROSS-Origin Resource Sharing (CORS) - Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Additional security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
    CSRF_COOKIE_HTTPONLY = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


APPEND_SLASH = True


# MINIO SETTINGS
if AWS_STORAGE_BUCKET_NAME := os.getenv("AWS_STORAGE_BUCKET_NAME"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    # AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv(
        "AWS_S3_ENDPOINT_URL"
    )  # Use container name if on Docker network

    AWS_S3_FILE_OVERWRITE = True
    # AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')  # or your custom value
    AWS_QUERYSTRING_AUTH = False  # So uploaded files have public URLs
