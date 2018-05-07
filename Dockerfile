ARG MOLO_VERSION=6
FROM praekeltfoundation/molo-bootstrap:${MOLO_VERSION}-onbuild

ENV DJANGO_SETTINGS_MODULE=gem.settings.docker \
    CELERY_APP=gem

RUN apt-get update && apt-get install -y netcat git

RUN pip install -r requirements.txt --src /usr/local/src

RUN LANGUAGE_CODE=en SECRET_KEY=compilemessages-key django-admin compilemessages && \
    SECRET_KEY=collectstatic-key django-admin collectstatic --noinput && \
    SECRET_KEY=compress-key django-admin compress

CMD ["gem.wsgi:application", "--timeout", "1800"]
