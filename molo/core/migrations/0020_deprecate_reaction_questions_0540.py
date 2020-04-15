# Generated by Django 2.2.7 on 2020-03-27 05:40

from django.db import migrations, models
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('wagtailforms', '0003_capitalizeverbose'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('core', '0019_add_is_service_aggregator'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArticlePageReactionQuestions',
        ),
        migrations.DeleteModel(
            name='ReactionQuestion',
        ),
        migrations.DeleteModel(
            name='ReactionQuestionChoice',
        ),
        migrations.DeleteModel(
            name='ReactionQuestionIndexPage',
        ),
        migrations.DeleteModel(
            name='ReactionQuestionResponse',
        ),
    ]
