"""
Django settings for betterhtwk2ical project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

from config import SECRETS
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRETS.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(SECRETS.get("DEBUG") or 0)

# 'ALLOWED_HOSTS' should be a single string of hosts with a space between each.
ALLOWED_HOSTS = SECRETS.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    'myapp1.apps.MyApp1Config',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'pipeline.middleware.MinifyHTMLMiddleware',  # Ensure that it comes after any middleware which modifies your HTML
]

ROOT_URLCONF = 'betterhtwk2ical.urls'

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

WSGI_APPLICATION = 'betterhtwk2ical.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'host':     SECRETS.get("DB.HOST"),
            'port':     SECRETS.get("DB.PORT"),
            'user':     SECRETS.get("DB.USER"),
            'password': SECRETS.get("DB.PASSWORD"),
        },
        'NAME': SECRETS.get("DB.NAME"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'de'

LANGUAGES = [
    ('de', _('Deutsch')),
    ('en', _('Englisch')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'CET'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_URL is the URL you users' browsers will request
STATIC_URL = 'static/'

# STATIC_ROOT is where Django collects your static files
STATIC_ROOT = BASE_DIR / 'static'

# Use ManifestStaticFilesStorage for better updating static files
STATICFILES_STORAGE = 'pipeline.storage.PipelineManifestStorage'

STATICFILES_DIRS = [
    "vendor",
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE = {
    'COMPILERS': ('pipeline.compilers.less.LessCompiler',),
    'LESS_BINARY': (BASE_DIR / (
            'node_modules/.bin/lessc' + ('.cmd' if int(SECRETS.get("WINDOWS")) == 1 else '')
    )).as_posix(),
    'YUGLIFY_BINARY': (BASE_DIR / (
            'node_modules/.bin/yuglify' + ('.cmd' if int(SECRETS.get("WINDOWS")) == 1 else '')
    )).as_posix(),
    # 'JS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    # 'CSS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'STYLESHEETS': {
        'application': {
            'source_filenames': (
                'assets/stylesheets/jquery.ui.theme.css',
                'assets/stylesheets/jquery.ui.core.css',
                'assets/stylesheets/jquery.ui.autocomplete.css',
                'assets/javascripts/bootstrap/css/bootstrap.css',
                'myapp1/stylesheets/bootstrap_and_overrides.css.less',
            ),
            'output_filename': 'application.css',
        },
    },
    'JAVASCRIPT': {
        'application': {
            'source_filenames': (
                'myapp1/javascripts/*.js',
                'assets/javascripts/jquery.cookie.js',
                'assets/javascripts/bootstrap/js/bootstrap.min.js',
                'assets/javascripts/bootstrap/js/bootstrap.min.js',
                'assets/javascripts/jquery-ui.min.js',
            ),
            'output_filename': 'application.js',
        }
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
