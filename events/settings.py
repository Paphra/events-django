"""
Django settings for events project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*67(t#lk)6l(9hm_f_9!pw@5vo=5wfce^xl)5%$zlu_%)o4+va'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'events.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
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

WSGI_APPLICATION = 'events.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'events',
        'USER': 'Paphra',
        'PASSWORD': 'Pephreto21',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Deployment 
#===========
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)
#============

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# location of static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# deploymnet STATIC_ROOT = /var/www/example.com

# Custom Settings

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Base url to serve media files
MEDIA_URL = '/media/'

# Path where media is stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


# django summernote
INSTALLED_APPS += ('django_summernote',)
#SUMMERNOTE_THEME = 'bs4'  # Show summernote with Bootstrap4

#sitemaps
INSTALLED_APPS += ('django.contrib.sitemaps',)
X_FRAME_OPTIONS = 'SAMEORIGIN'

SUMMERNOTE_CONFIG = {
    'width': '100%',
    # You can disable attachment feature.
    'disable_attachment': True,
}

# PesaPal
#====

PESAPAL_DEMO = True
#PESAPAL_DEMO=False

if PESAPAL_DEMO:
    # demo
    PESAPAL_CONSUMER_KEY = "nxE8AeoNZXU8BkeB+A1jCQqvI0KFt/8V"
    PESAPAL_CONSUMER_SECRET = "vVV8l9Lm2W1YvqepJpYaeetBqC4="
    PESAPAL_IFRAME_LINK = 'http://demo.pesapal.com/api/PostPesapalDirectOrderV4'
    PESAPAL_QUERY_STATUS_LINK = 'http://demo.pesapal.com/API/QueryPaymentDetails'
else:
    # production
    PESAPAL_IFRAME_LINK = 'https://www.pesapal.com/api/PostPesapalDirectOrderV4'
    PESAPAL_QUERY_STATUS_LINK =	'https://www.pesapal.com/API/QueryPaymentDetails'
    PESAPAL_CONSUMER_KEY = 'oGQJZ1Ew1MDw4MSoyYv0mgZVhxSBMXCn'
    PESAPAL_CONSUMER_SECRET = 'bYrfSMxFGNUWEZ7DUzw3fX9KHY4='

#=====

# Deplyment
#============
ALLOWED_HOSTS = [
    'ultimatesports.herokuapp.com',
    '0.0.0.0', 'localhost', 
    '127.0.0.1',
]

DEBUG = False

if DEBUG
    PESAPAL_CALLBACK = "http://127.0.0.1:8000/booking"
else:
    PESAPAL_CALLBACK = ALLOWED_HOSTS[0] + "/booking"

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEBUG_PROPAGATE_EXCEPTIONS = True
