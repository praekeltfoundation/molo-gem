from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from django_comments.models import Comment


class Command(BaseCommand):
    "Remove the given string from the comments"

    def add_arguments(self, parser):
        parser.add_argument('string', type=str)

    def handle(self, *args, **options):
        string = options.get('string', None)
        for comment in Comment.objects.all().iterator():
            old_comment = comment.comment
            new_comment = old_comment.replace(string, "")
            comment.comment = new_comment
            comment.save()

