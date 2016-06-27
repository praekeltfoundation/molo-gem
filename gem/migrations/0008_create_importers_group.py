# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_import_group(apps, schema_editor):
    from molo.core.models import Main
    main = Main.objects.all().first()

    if main:
        Group = apps.get_model('auth.Group')
        Group.objects.get_or_create(name='Universal Core Importers')


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0007_move_pages_to_index_pages'),
    ]

    operations = [
        migrations.RunPython(create_import_group),
    ]
