"""
Django settings for delivery_system project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(xeyg#v3j4yw4sinw7_vgpk83-dn!qr&3ona3$^0#rx&y2a-wd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'daphne',                       # https://channels.readthedocs.io/en/stable/installation.html
    'channels',                     # https://pypi.org/project/channels/
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'users.apps.UsersConfig',
    # 'parcels.apps.ParcelsConfig',
    'package_request',
    'stations',
    'management',
    'chatbot',
    'notifications',
    
    
    'phonenumber_field',                    #   https://pypi.org/project/django-phonenumber-field/
    'places',                               #   https://pypi.org/project/dj-places/
    # 'django_pdb'
    # 'driver'
    
    'bootstrap5',
    'rosetta'
]

#Middleware should go after SessionMiddleware, CacheMiddleware, but before CommonMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
]

ROOT_URLCONF = 'delivery_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n'
            ],
        },
    },
]

WSGI_APPLICATION = 'delivery_system.wsgi.application'
ASGI_APPLICATION = 'delivery_system.asgi.application'

CHANNEL_LAYERS = {
    'default' : {
        'BACKEND' : "channels.layers.InMemoryChannelLayer"
    }
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True

LANGUAGES = [
  ('en', _('English')),
  ('zh-hant', _('Chinese')),
]

LOCALE_PATHS = [
  os.path.join(BASE_DIR, 'locale')
]

# Email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'devtestuserproject@gmail.com'

EMAIL_HOST_PASSWORD = 'oildlnyofgezgynh'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


MEDIA_URL = '/images/'

MEDIA_ROOT = BASE_DIR / 'static/images'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model

AUTH_USER_MODEL = 'users.User'


# Google Maps API Settings
PLACES_MAPS_API_KEY=''
PLACES_MAP_WIDGET_HEIGHT=480
PLACES_MAP_OPTIONS='{"center": { "lat": 23.993356020228287, "lng": 121.60125981977495 }, "zoom": 15}'
PLACES_MARKER_OPTIONS='{"draggable": true, "clickable": true}'


# Django session Configurations
SESSION_EXPIRE_SECONDS = 172800                         # 48 hours = 172800
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True               # session will expire after last activity
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60    # grouping by minutes
# SESSION_COOKIE_AGE = 60*30                              # 30 minutes         
SESSION_TIMEOUT_REDIRECT = '/login/'                    # route to login if timeout is detected
SESSION_EXPIRE_AT_BROWSER_CLOSE = True