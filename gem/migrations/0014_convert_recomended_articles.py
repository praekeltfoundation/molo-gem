# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_recomended_article(article, block):
    from molo.core.models import ArticlePage, ArticlePageRecommendedSections
    # get the article page
    hyperlinked_article = ArticlePage.objects.get(
        id=block['value'])

    # check if recomended article exists already

    rec_articles = [ra.recommended_article for ra in article.recommended_articles.all()]

    if hyperlinked_article not in rec_articles:
        # create recomended section
        ArticlePageRecommendedSections(
            page=article,
            recommended_article=hyperlinked_article).save()

        #  enable parent section
        (article.get_parent()
            .specific.enable_recommended_section) = True


def convert_articles(apps, schema_editor):
    '''
    Derived from https://github.com/wagtail/wagtail/issues/2110
    '''
    from molo.core.models import ArticlePage
    from wagtail.wagtailcore.blocks import StreamValue

    articles = ArticlePage.objects.all()

    for article in articles:
        stream_data = []
        for block in article.body.stream_data:
            if block['type'] == 'page':
                create_recomended_article(article, block)
            else:
                # add block to new stream_data
                stream_data.append(block)

        stream_block = article.body.stream_block
        article.body = StreamValue(stream_block, stream_data, is_lazy=True)
        article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0013_gemsettings_moderator_name'),
    ]

    operations = [
        migrations.RunPython(convert_articles),
    ]
