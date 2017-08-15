from django.conf import settings
from fcm_django.models import FCMDevice
from fcm_django.fcm import FCMError


def send_notification_to_fcm(
        user, title, content, object_id, use_notification=True):
    if not hasattr(settings, 'FCM_DJANGO_SETTINGS'):
        return False
    reg_id = user.registration_token
    if not reg_id:
        return False
    device, created = FCMDevice.objects.get_or_create(
        registration_id=reg_id, defaults={
            'user': user,
            'name': user.alias, 'type': 'web'})
    data = {'type': title, 'payload': {
        'object_id': object_id, 'content': content}}

    try:
        print device.send_message(data=data)
    except FCMError:
        return False
    try:
        if use_notification:
            device.send_message(body=content)
    except FCMError:
        return False
