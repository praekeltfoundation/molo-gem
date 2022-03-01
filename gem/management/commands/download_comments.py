import json
from django.core.management.base import BaseCommand
from molo.commenting.models import MoloComment


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        comments = MoloComment.objects.all()

        for comment in comments:
            comment_data = {}
            if comment.parent:
                comment_data["parent_pk"] = comment.parent.pk
                comment_data["parent_pk"] = comment.parent.slug
                comment_data["parent_locale"] = comment.language.locales
            comment_data["wagtail_site"] = comment.wagtail_site.pk
            if comment.user:
                comment_data["username"] = comment.user.username
                comment_data["user_is_staff"] = comment.user.is_staff
            comment_data["flag_count"] = comment.flags.all().count()
            comment_data["is_removed"] = comment.is_removed
            comment_data["comment"] = comment.comment
            comment_data["submit_date"] = str(comment.submit_date)
            comment_data["is_public"] = comment.is_public
            data[comment.pk] = comment_data

        with open('comments.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
