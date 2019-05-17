from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index


class VideosIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Add extra variables and return the updated context
        context['videos_entries'] = VideosIndexPage.objects.live()
        context['latest_video'] = VideosIndexPage.objects.latest('id')
        return context


class VideosPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    videourl = models.CharField(max_length=250,null=True)
    image = models.ImageField(null=True, blank=True, upload_to='media')

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('videourl'),
        ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        FieldPanel('videourl'),
        FieldPanel('image'),
        ]

    def get_context(self, request):
       context = super(VideosPage, self).get_context(request)
       # import pdb
       # pdb.set_trace()
       context['video_entries'] = VideosPage.objects.order_by('date')
       return context
