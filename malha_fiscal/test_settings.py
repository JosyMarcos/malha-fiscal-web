from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'test-only-secret-key-django-malha-fiscal'
DEBUG = True
ALLOWED_HOSTS = ['*']
AUTH_PASSWORD_VALIDATORS = []
