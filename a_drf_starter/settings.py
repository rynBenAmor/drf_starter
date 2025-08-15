

from pathlib import Path
from decouple import config


# * ----------------------------------------------------------------------------------------------------------
# * variable setup
# * ----------------------------------------------------------------------------------------------------------
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_SECRET_KEY = config('DJANGO_SECRET_KEY', cast=str)
DJANGO_IS_PRODUCTION = config('DJANGO_IS_PRODUCTION', default=True, cast=bool)
DB_TYPE = config('DB_TYPE')
DJANGO_CUSTOM_ADMIN_URL ="admin/" # if using the admin at all

print(
    "=============================\n"
    f"  Production: {DJANGO_IS_PRODUCTION}\n"
    f"  Database:   {DB_TYPE}\n"
    "============================="
)


# * ----------------------------------------------------------------------------------------------------
# * Security settings 
# * ----------------------------------------------------------------------------------------------------
DEBUG = not DJANGO_IS_PRODUCTION
SECRET_KEY = DJANGO_SECRET_KEY

ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='').split(',') if h.strip()]
INTERNAL_IPS = ["127.0.0.1"]

# CSRF & Session security
CSRF_COOKIE_HTTPONLY = False  # !important for the js frontend to have this accessible
CSRF_COOKIE_SECURE = DJANGO_IS_PRODUCTION
SESSION_COOKIE_SECURE = DJANGO_IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 60  # 60 days

# SSL / HSTS
SECURE_SSL_REDIRECT = DJANGO_IS_PRODUCTION
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


if DJANGO_IS_PRODUCTION :
    ADMINS = [
        ("Administration", config('DJANGO_ADMIN_EMAIL_1', cast=str)),
    ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # * 3rd party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # * my apps
    'accounts',
]

MIDDLEWARE = [
    # * 3rd party
    "corsheaders.middleware.CorsMiddleware",
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # * custom middlewares
    'accounts.middlewares.InjectCsrfCookieMiddleware',
]

ROOT_URLCONF = 'a_drf_starter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'a_drf_starter.wsgi.application'


# * ----------------------------------------------------------------------------------------------------------
# * Database
# * ----------------------------------------------------------------------------------------------------------

if DB_TYPE == 'sqlite':  # Switch to SQLite

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:  # Switch to PostgreSQL

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='5432', cast=int),
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# * ----------------------------------------------------------------------------------------------------------
# * Static files (CSS, JavaScript, Images)
# * ----------------------------------------------------------------------------------------------------------

# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'accounts.User'



# * ----------------------------------------------------------------------------------------------------------
# * Mailing
# * ----------------------------------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email server configuration
if DJANGO_IS_PRODUCTION:
    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True

    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# * ======================================================================
# * DRF / JWT
# * ======================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.authentication.CookieJwtAuthentication',
        'rest_framework.authentication.SessionAuthentication',  #  TODO (remove if debugging with Postman): needed for CSRF enforcement
    ),

}
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}


# * ======================================================================
# * CORS / CSRF
# * ======================================================================

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True # doesn't matter in dev
else:
    CORS_ALLOWED_ORIGINS = [h.strip() for h in config('CORS_ALLOWED_ORIGINS', default='').split(',') if h.strip()]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

CORS_ALLOW_CREDENTIALS =True




