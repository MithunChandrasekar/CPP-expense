"""
Django settings for expense project.

Generated by 'django-admin startproject' using Django 2.1.15.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path
import watchtower
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent


#ALLOWED_HOSTS = ['*']
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
#ALLOWED_HOSTS = ['expense-application-env.eba-7v85kh5i.us-east-1.elasticbeanstalk.com']
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'Vj9Q0dh7TMLJKM1x1jetBHvIY04DdO__WkCCKSoaRchE2fF4niQ1ZNzj-qhV-r76VeA'

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
#DEBUG = False
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True


CSRF_TRUSTED_ORIGINS = [
    'https://15155f23e5ef4afa812dfc93aaef473f.vfs.cloud9.us-east-1.amazonaws.com',
    'http://expense-application-env.eba-7v85kh5i.us-east-1.elasticbeanstalk.com/',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "crispy_forms",
    "crispy_bootstrap5",
    'user'
]


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'expense.urls'

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

WSGI_APPLICATION = 'expense.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True




# settings.py

# Add S3 configuration

AWS_STORAGE_BUCKET_NAME = 'my-expense-app-bucket'
AWS_S3_REGION_NAME = 'us-east-1'  # Replace with your region (if different)
AWS_REGION = 'us-east-1'  # Ensure it matches AWS_S3_REGION_NAME
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media URL for accessing files
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'

# Media URL for accessing file

# Optional: For static files (CSS/JS), add this if needed:
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'


STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field


#this was not there on default but was added when i brought to cloud9
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AWS_REGION_NAME = 'us-east-1'  # Replace with your region
AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:973195829891:user-notifications'  # Replace with your Topic ARN



#SMTP Configuration

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_USE_TLS = 'True'

EMAIL_HOST_USER = 'djangomitz@gmail.com'
EMAIL_HOST_PASSWORD = 'wffk dmkx tyen nqre'
DEFAULT_FROM_EMAIL = 'djangomitz@gmail.com'


'''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'watchtower': {
            'level': 'INFO',
            'class': 'watchtower.CloudWatchLogHandler',
            'log_group': 'expense-logs',  # Use your log group name
        },
    },
    'loggers': {
        'django': {
            'handlers': ['watchtower'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
'''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'your_app_name': {  # Replace with the actual app name
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
