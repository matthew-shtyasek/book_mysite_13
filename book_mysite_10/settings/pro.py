from .base import *

DEBUG = False

ADMINS = (
    ('Shtyasek M', 'shtyasek2003@mail.ru'),
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': '123456',
    },
}

# export DJANGO_SETTINGS_MODULE=book_mysite_10.settings.pro - env var for current console session
# python manage.py migrate --settings=book_mysite_10.settings.pro - for current program

#python manage.py check --deploy - check project for deploy (this command can run without deploy flag)
