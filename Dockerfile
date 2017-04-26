FROM praekeltfoundation/molo-bootstrap:5.1.0-onbuild

ENV DJANGO_SETTINGS_MODULE=gem.settings.docker \
    CELERY_APP=gem \
    CELERY_WORKER=1 \
    CELERY_BEAT=1

RUN LANGUAGE_CODE=en django-admin compilemessages && \
    django-admin collectstatic --noinput && \
    django-admin compress

CMD ["gem.wsgi:application", "--timeout", "1800"]
