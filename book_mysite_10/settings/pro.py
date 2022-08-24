from .base import *

DEBUG = False

ADMINS = (
    ('Shtyasek M', 'shtyasek2003@mail.ru'),
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {},
}

# export DJANGO_SETTINGS_MODULE=book_mysite_10.settings.pro - env var for current console session
# python manage.py migrate --settings=book_mysite_10.settings.pro - for current program
