from .base import *  # noqa


ALLOWED_HOSTS = [
    'localhost',
    '.localhost',
]

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa
except ImportError:
    pass

try:
    from secrets import *  # noqa
except ImportError:
    pass
