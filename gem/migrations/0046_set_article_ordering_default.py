from django.db import migrations

from molo.core.models import SiteSettings
from wagtail.core.models import Site


def set_article_default_ordering(apps, schema_editor):
    for site in Site.objects.all():
        settings = SiteSettings.for_site(site)
        settings.article_ordering_within_section = 'cms_default_sorting'
        settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0045_auto_20210107_1241'),
    ]

    operations = [
        migrations.RunPython(set_article_default_ordering)
    ]
