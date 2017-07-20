from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from .views import create


@hooks.register('register_admin_urls')
def register_csv_group_creation_urlconf():
    return [
        url('csv-group-creation/$', create, name='csv-group-creation'),
    ]


@hooks.register('register_settings_menu_item')
def register_csv_group_creation_menu_item():
    return MenuItem(
        _('CSV group creation'),
        reverse('csv-group-creation'),
        classnames='icon icon-group', order=601)
