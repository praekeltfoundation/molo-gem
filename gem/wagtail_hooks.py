from gem.admin import GemCommentModelAdmin
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.wagtailcore import hooks

modeladmin_register(GemCommentModelAdmin)


@hooks.register('construct_main_menu')
def hide_duplicate_comments_menu_item(request, menu_items):
    menu_items[:] = [
        item for item in menu_items if not item.name == 'comments']
