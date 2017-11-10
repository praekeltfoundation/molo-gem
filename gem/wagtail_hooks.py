from gem.admin import GemFrontendUsersModelAdmin
from wagtail.contrib.modeladmin.options import modeladmin_register


modeladmin_register(GemFrontendUsersModelAdmin)


@hooks.register('insert_global_admin_js')
def global_admin_js():
    js_files = [
        'js/modeladmin/index.js',
    ]

    js_includes = format_html_join(
        '\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes
