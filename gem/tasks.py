from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .celery import app


@app.task(ignore_result=True)
def send_export_email_gem(recipient, arguments):
    from gem.admin import GemFrontendUsersResource
    csvfile = GemFrontendUsersResource().export(
        User.objects.filter(is_staff=False, **arguments)).csv
    subject = 'Molo export: %s' % settings.SITE_NAME
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, '', from_email, (recipient,))
    msg.attach(
        'Molo_export_%s.csv' % settings.SITE_NAME,
        csvfile, 'text/csv')
    msg.send()
