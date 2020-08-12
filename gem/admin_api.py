from django.conf.urls import url

from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.admin.api.endpoints import PagesAdminAPIEndpoint
from wagtail.api.v2.utils import \
    BadRequestError, parse_fields_parameter, \
    filter_page_type, page_models_from_string


class GemPagesAdminApi(PagesAdminAPIEndpoint):
    def get_queryset(self):
        request = self.request

        # Allow pages to be filtered to a specific type
        try:
            models = page_models_from_string(
                request.GET.get('type', 'wagtailcore.Page'))
        except (LookupError, ValueError):
            raise BadRequestError("type doesn't exist")

        if not models:
            models = [Page]

        if len(models) == 1:
            print(request.GET, 'if', '*' * 100)
            self.queryset = models[0].objects.exclude(depth=1).all()
        else:
            print(request.GET, 'else', '=' * 100)
            self.queryset = filter_page_type(
                Page.objects.exclude(depth=1).all(), models)

        return self.queryset

    def get_serializer_class(self):
        if self.action == 'listing_view':
            show_details = False
            model = getattr(self, 'queryset', self.get_queryset()).model
        else:
            # Allow "detail_only" (eg parent) fields on detail view
            show_details = True
            model = type(self.get_object())

        # Fields
        try:
            fields_config = parse_fields_parameter(
                self.request.GET.get('fields', []))
        except ValueError as e:
            raise BadRequestError("fields error: %s" % str(e))

        return self._get_serializer_class(
            self.request.wagtailapi_router,
            model, fields_config, show_details=show_details
        )


admin_api = WagtailAPIRouter('gem_wagtailadmin_api_v1')
admin_api.register_endpoint('pages', GemPagesAdminApi)

for fn in hooks.get_hooks('construct_admin_api'):
    fn(admin_api)

urlpatterns = [
    url(r'^v2beta/', admin_api.urls),
]
