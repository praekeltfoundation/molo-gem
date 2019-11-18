# flake8: noqa: E128
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-24 12:20
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType
from django.core.management.sql import emit_post_migrate_signal


def add_molo_forms_permissions(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    emit_post_migrate_signal(2, False, db_alias)

    Group = apps.get_model('auth.Group')
    Permission = apps.get_model('auth.Permission')
    GroupPagePermission = apps.get_model('wagtailcore.GroupPagePermission')
    FormsIndexPage = apps.get_model('forms.FormsIndexPage')

    # **** Get IndexPages ****
    forms = FormsIndexPage.objects.filter(slug='molo-forms').all()

    # **** Get Permission ****

    # Wagtail
    access_admin = get_permission(Permission, 'access_admin')

    # Forms
    FormsSegmentUserGroup, created = ContentType.objects.get_or_create(
        app_label='forms', model='FormsSegmentUserGroup')

    Permission.objects.create(
        name='add_segmentusergroup',
        codename='add_segmentusergroup',
        content_type_id=FormsSegmentUserGroup.pk)

    Permission.objects.create(
        name='change_segmentusergroup',
        codename='change_segmentusergroup',
        content_type_id=FormsSegmentUserGroup.pk)

    Permission.objects.create(
        name='delete_segmentusergroup',
        codename='delete_segmentusergroup',
        content_type_id=FormsSegmentUserGroup.pk)

    add_segmentusergroup = get_permission(
        Permission, 'add_segmentusergroup')
    change_segmentusergroup = get_permission(
        Permission, 'change_segmentusergroup')
    delete_segmentusergroup = get_permission(
        Permission, 'delete_segmentusergroup')

    add_segment = get_permission(Permission, 'add_segment')
    change_segment = get_permission(Permission, 'change_segment')
    delete_segment = get_permission(Permission, 'delete_segment')


    # Wagtail Page permission
    page_permission_types = ('add', 'edit', 'publish', 'bulk_delete', 'lock')

    # **** Add wagtail groups permission ****

    # <----- Product Admin ----->
    product_admin_group = get_or_create_group(Group, 'product_admin')
    # Page permissions
    create_page_permission(
        GroupPagePermission, product_admin_group, forms, page_permission_types)

    # <----- Data Admin ----->
    data_admin_group = get_or_create_group(Group, 'data_admin')
    # Page permissions
    create_page_permission(
        GroupPagePermission, data_admin_group, forms, page_permission_types)

    # <----- Content Admin ----->
    content_admin_group = get_or_create_group(Group, 'content_admin')
    # Page permissions
    create_page_permission(
        GroupPagePermission, content_admin_group, forms, page_permission_types)


def get_or_create_group(Group, group_name):
    group, _created = Group.objects.get_or_create(name=group_name)
    return group


def get_permission(Permission, code_name):
    return Permission.objects.get(codename=code_name)


def create_page_permission(GroupPagePermission, group, pages, page_permission_type):
    for page in pages.iterator():
        for permission_type in page_permission_type:
            GroupPagePermission.objects.get_or_create(
                group=group, page=page, permission_type=permission_type)


class Migration(migrations.Migration):
    dependencies = [
        ('gem', '0037_remove_content_editor_survey_permissions'),
        ('core', '0077_molo_page'),
        ('forms', '0002_create_forms_index_page'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('wagtailadmin', '0001_create_admin_access_permissions'),
        ('wagtailusers', '0005_make_related_name_wagtail_specific'),
        ('sites', '0002_alter_domain_unique'),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.RunPython(add_molo_forms_permissions),
    ]