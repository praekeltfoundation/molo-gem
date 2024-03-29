import json
from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage
from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        articles = ArticlePage.objects.all()
        count = articles.count()
        articles = articles.order_by('-last_published_at').iterator()
        self.stdout.write(self.style.WARNING(
            "Articles Found: " + str(count)))
        for val, article in enumerate(articles):
            self.stdout.write(self.style.WARNING(
                "Busy With: " + str(val + 1)))
            if not article.language:
                self.stdout.write(self.style.WARNING(
                    "Articles has no language: " + str(article.pk)))
                continue
            article_data = {}
            article_data["title"] = article.title
            article_data["slug"] = article.slug
            article_data["type"] = article.specific.exact_type()
            article_data["locale"] = article.language.locale
            article_data["live"] = article.live
            article_data["featured_in_homepage"] = article.featured_in_homepage
            article_data["uuid"] = article.uuid
            article_data["main_title"] = article.get_site().root_page.title
            article_data["translation_pks"] = [page.pk for page in article.translated_pages.all()]
            article_data["subtitle"] = article.subtitle
            if article.image:
                article_data["image_name"] = article.image.title
                article_data["image_url"] = article.image.usage_url
                article_data["image_filename"] = article.image.filename
            body_string = ''
            for block in article.body:
                rendered = block.render_as_block()
                if block.block_type == 'heading':
                    rendered = "<h2>" + block.render_as_block() + "</h2>"
                if block.block_type == 'numbered_list':
                    rendered = block.render_as_block().replace("ul", "ol")
                body_string += (rendered + "\n")
            article_data["body"] = body_string
            article_data["featured_in_homepage"] = article.featured_in_homepage
            try:
                if article.get_parent_section():
                    article_data["parent_section_slug"] = article.get_parent_section(locale=article_data["locale"]).specific.slug
                    article_data["parent_section_locale"] = article.get_parent_section(locale=article_data["locale"]).specific.language.locale
            except:
                pass
            data[article.pk] = article_data

        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS("Download Completed"))
