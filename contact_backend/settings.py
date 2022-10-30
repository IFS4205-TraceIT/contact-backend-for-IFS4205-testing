"""
Django settings for contact_backend project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get('DJANGO_DEBUG') == "True")

# Vault client connection and initialization settings.
# See https://hvac.readthedocs.io/en/stable/source/hvac_v1.html#hvac.v1.Client.__init__
VAULT_SETTINGS = {
    'url': os.environ['VAULT_ADDR'],
    'token': os.environ['VAULT_TOKEN'],
    'verify': False if DEBUG else os.environ.get('VAULT_ROOT_CA_FILE'),
    'cert': None if DEBUG else (os.environ.get('VAULT_CLIENT_CERT_FILE'), os.environ.get('VAULT_CLIENT_KEY_FILE')),
}
VAULT_TEMP_ID_KEY_PATH = 'contacts/temp_id_key'


CORS_ALLOW_ALL_ORIGINS = DEBUG

ALLOWED_HOSTS = ['traceit-04-i.comp.nus.edu.sg', '.localhost', '127.0.0.1', '[::1]'] if DEBUG else ['traceit-04-i.comp.nus.edu.sg']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'accounts.apps.AccountsConfig',
    'contacts.apps.ContactsConfig',
    'buildings.apps.BuildingsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'contact_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'contact_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ['POSTGRES_AUTH_HOST'],
        'PORT': os.environ['POSTGRES_AUTH_PORT'],
        'NAME': os.environ['POSTGRES_AUTH_DB'],
        'USER': os.environ['POSTGRES_AUTH_USER'],
        'PASSWORD': os.environ['POSTGRES_AUTH_PASSWORD'],
        'OPTIONS': {} if DEBUG else {
            'sslmode': 'verify-ca',
            'sslcert': os.environ['POSTGRES_AUTH_SSL_CERT'],
            'sslkey': os.environ['POSTGRES_AUTH_SSL_KEY'],
            'sslrootcert': os.environ['POSTGRES_AUTH_SSL_ROOT_CERT'],
        },
    },
    'main_db': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT'],
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'OPTIONS': {} if DEBUG else {
            'sslmode': 'verify-ca',
            'sslcert': os.environ['POSTGRES_SSL_CERT'],
            'sslkey': os.environ['POSTGRES_SSL_KEY'],
            'sslrootcert': os.environ['POSTGRES_SSL_ROOT_CERT'],
        },
    }
}

#'database_routers.main.MainRouter'
DATABASE_ROUTERS = ['database_routers.default.DefaultRouter','database_routers.main.MainRouter']


# DEFAULT USER MODEL
AUTH_USER_MODEL = 'accounts.AuthUser'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'accounts.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': ('accounts.authentication.TwoFactorAuthentication',),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '1000/day',
    },
}

# Simple JWT Settings
# See https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': not DEBUG,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(message)s',
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'loki': {
            'level': 'INFO',
            'class': 'logging_loki.LokiHandler',
            'url': 'https://logs-prod-011.grafana.net/loki/api/v1/push',
            'tags': {'app': 'contact-backend'},
            'auth': ('', '') if DEBUG else ('308685', os.environ['LOKI_PASSWD']),
            'version': '1',
            'formatter': 'json',
        },
    },
    'loggers': {
        'loki': {
            'handlers': ['console'] if DEBUG else ['console', 'loki'],
            'level': 'INFO',
            'propagate': DEBUG,
        }
    }
}