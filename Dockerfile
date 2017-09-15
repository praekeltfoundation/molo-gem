FROM praekeltfoundation/molo-bootstrap:5.15.0-onbuild

ENV DJANGO_SETTINGS_MODULE=gem.settings.docker \
    CELERY_APP=gem

RUN LANGUAGE_CODE=en django-admin compilemessages && \
    django-admin collectstatic --noinput && \
    django-admin compress

CMD ["gem.wsgi:application", "--timeout", "1800"]
