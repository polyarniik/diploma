import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR.joinpath("templates")
MEDIA_ROOT = BASE_DIR.joinpath("media")
STATICFILES_DIRS = [
    BASE_DIR.joinpath("static"),
]

STATIC_URL = "static/"
MEDIA_URL = "/media/"
LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/repositories/"
SECRET_KEY = os.environ.get("DJANGO__SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
AUTH_USER_MODEL = "users.User"
PAGE_SIZE = 25
# CELERY
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TRACK_STARTED = True
BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_BROKER_URL = os.getenv("DSN__RABBITMQ")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LIBRARIES_APPS = [
    "rest_framework",
]
THIRD_PARTY_APPS = [
    "repositories",
    "users",
]

INSTALLED_APPS += LIBRARIES_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(env="DSN__DATABASE", conn_max_age=None),
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"]}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATETIME_FORMAT = "%H:%M:%s - %d.%m.%Y"
