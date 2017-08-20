"""
Various importers for the different content types
"""
import math
import json
import requests
from io import BytesIO

from django.core.files.images import ImageFile

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image

from molo.core.models import (
    Languages,
    SiteLanguageRelation,
    ArticlePage,
    SectionPage,
    FooterPage,
    BannerPage,
    Tag,
    ArticlePageRecommendedSections,
    ArticlePageRelatedSections,
    PageTranslation,
    ArticlePageTags,
    SectionPageTags,
    ImportableMixin,
)
from molo.core.api.constants import (
    API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT
)
from molo.core.api.errors import (
    RecordOverwriteError,
    ReferenceUnimportedContent,
)
from molo.core.utils import (
    get_image_hash,
    separate_fields,
    add_json_dump,
    add_list_of_things,
)

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


# functions used to find images
def get_image_attributes(base_url, image_id):
    image_attrs = requests.get(
        base_url + API_IMAGES_ENDPOINT + str(image_id)
    ).json()
    return image_attrs


def get_image(base_url, image_id):
    # TODO: guard against non-existent images
    image_attributes = get_image_attributes(base_url, image_id)
    image_file = requests.get(image_attributes["file"])
    image = Image(
        title=image_attributes["title"],
        file=ImageFile(
            BytesIO(image_file.content), name=image_attributes["title"]
        )
    )
    image.save()
    return image


def list_of_objects_from_api(url):
        '''
        API only serves 20 pages by default
        This fetches info on all of items and return them as a list

        Assumption: limit of API is not less than 20
        '''
        response = requests.get(url)

        content = json.loads(response.content)
        count = content["meta"]["total_count"]

        if count <= 20:
            return content["items"]
        else:
            items = [] + content["items"]
            num_requests = int(math.ceil(count // 20))

            for i in range(1, num_requests + 1):
                paginated_url = "{}?limit=20&offset={}".format(
                    url, str(i * 20))
                paginated_response = requests.get(paginated_url)
                items = items + json.loads(paginated_response.content)["items"]
        return items


def record_foreign_relation(field, key, record_keeper, id_key="id"):
    '''
    returns a function with the attributes necessary to
    correctly reference the necessary objects, to correctly record
    the relationship between a page and its foreign foreign-key pages
    '''
    def record_relationship(nested_fields, page_id):
        if ((field in nested_fields) and nested_fields[field]):
            record_keeper[page_id] = []
            for thing in nested_fields[field]:
                if thing[key]:
                    if thing[key][id_key]:
                        record_keeper[page_id].append(thing[key][id_key])
                    else:
                        print(
                            "key of: {} does not exist in thing[]".format(key))
                else:
                    print("key of: {} does not exist".format(key))
    return record_relationship


def record_foreign_key(field, record_keeper, id_key="id"):
    '''
    returns a function with the attributes necessary to replicate
    a foreign key relation
    '''
    def _record_foreign_key(nested_fields, page_id):
        if ((field in nested_fields) and nested_fields[field]):
            record_keeper[page_id] = nested_fields[field][id_key]
    return _record_foreign_key


def attach_image(field, image_map):
    '''
    Returns a function that attaches an image to page if it exists

    Assumes that images have already been imported
    otherwise will fail silently
    '''
    def _attach_image(nested_fields, page):
        if (field in nested_fields) and nested_fields[field]:
            foreign_image_id = nested_fields[field]["id"]
            try:
                local_image_id = image_map[foreign_image_id]
                local_image = Image.objects.get(id=local_image_id)
                setattr(page, field, local_image)
            except (KeyError, ObjectDoesNotExist):
                # TODO: log when page is not found
                pass
    return _attach_image


class PageImporter(object):

    def __init__(self, base_url=None, content=None, content_type=None):
        self._content_type = content_type
        self._fields = []
        self._content = content
        self._base_url = base_url

    def get_content_from_url(self, base_url):
        """
        Sections can have SectionPage and ArticlePage child objects.
        These have different fields, and thus have to be treated
        differently.
        """
        # assemble url
        base_url = base_url.rstrip("/")
        url = base_url + API_PAGES_ENDPOINT + "?type=" + self._content_type + \
            "&fields=" + ",".join(self._fields) + \
            "&order=latest_revision_created_at"

        # make request
        try:
            response = requests.get(url)
            self._base_url = base_url
            self._content = response.json()
            self._content = self._content["items"]
            return self._content
        except requests.exceptions.ConnectionError:
            return "No content could be found from {}. " \
                "Are you sure this is the correct URL?".format(base_url)
        except requests.exceptions.RequestException:
            return "Content could not be imported at this time. " \
                   "Please try again later."

    def content(self):
        if self._content:
            return self._content
        return []

    def save(self, indexes, parent_id):
        pass


class ArticlePageImporter(PageImporter):

    def __init__(self, base_url=None, content=None, content_type=None):
        super(ArticlePageImporter, self).__init__(
            base_url=base_url, content=content, content_type=content_type
        )
        self._content_type = "core.ArticlePage"
        self._fields = ArticlePage.get_api_fields()

    def save(self, indexes, parent_id):
        if self.content():
            parent = Page.objects.get(id=parent_id)
            for index in indexes:
                # Remove "id" and "meta" fields
                selected_article = self.content()[index]
                fields, nested_fields = separate_fields(selected_article)
                article = ArticlePage(**fields)

                # TODO: u'related_sections'
                # process the nested fields
                if ("tags" in nested_fields) and nested_fields["tags"]:
                    article.tags.add(", ".join(nested_fields["tags"]))

                if ("metadata_tags" in nested_fields) and \
                        nested_fields["metadata_tags"]:
                    article.metadata_tags.add(
                        ", ".join(nested_fields["metadata_tags"])
                    )

                if ("body" in nested_fields) and nested_fields["body"]:
                    article.body = json.dumps(nested_fields["body"])

                if ("image" in nested_fields) and nested_fields["image"]:
                    article.image = get_image(
                        self._base_url, nested_fields["image"]["id"]
                    )

                parent.add_child(instance=article)
                parent.save_revision().publish()


class SectionPageImporter(PageImporter):

    def __init__(self, base_url=None, content=None, content_type=None):
        super(SectionPageImporter, self).__init__(
            base_url=base_url, content=content, content_type=content_type
        )
        self._content_type = "core.SectionPage"
        self._fields = SectionPage.get_api_fields()

    def _save_item(self, item, parent):
        if item["meta"]["type"] == "core.SectionPage":
            flat_fields, nested_fields = separate_fields(item)
            child_section = SectionPage(**flat_fields)

            if ("image" in nested_fields) and nested_fields["image"]:
                child_section.image = get_image(
                    self._base_url, nested_fields["image"]["id"]
                )

            parent.add_child(instance=child_section)
            parent.save_revision().publish()
            return child_section

        elif item["meta"]["type"] == "core.ArticlePage":
            flat_fields, nested_fields = separate_fields(item)
            child_article = ArticlePage(**flat_fields)
            if ("tags" in nested_fields) and nested_fields["tags"]:
                child_article.tags.add(
                    ", ".join(nested_fields["tags"])
                )

            if ("metadata_tags" in nested_fields) and \
                    nested_fields["metadata_tags"]:
                child_article.metadata_tags.add(
                    ", ".join(nested_fields["metadata_tags"])
                )

            if ("body" in nested_fields) and nested_fields["body"]:
                child_article.body = json.dumps(nested_fields["body"])

            if ("image" in nested_fields) and nested_fields["image"]:
                child_article.image = get_image(
                    self._base_url, nested_fields["image"]["id"]
                )

            parent.add_child(instance=child_article)
            parent.save_revision().publish()
            return child_article

    def process_child_section(self, id, parent):
        response = requests.get(
            self._base_url + API_PAGES_ENDPOINT + str(id)
        ).json()
        ancestor = self._save_item(response, parent)
        if response["meta"]["children"]:
            for child_id in response["meta"]["children"]["items"]:
                self.process_child_section(child_id, ancestor)
        return ancestor

    def recursive_children(self, node):
        results = [node['id']]
        if len(node['children']) > 0:
            for child in node['children']:
                results.extend(self.recursive_children(child))
        return results

    def save(self, indexes, parent_id):
        """
        Save the selected section. This will save the selected section
        as well as its direct child pages obtained through the ?child_of
        query parameter. The ?descendant_of query parameter is probably
         better suited because it all pages under that part of the tree will
         be obtained. The problem , however, is that that will require being
         able to traverse the tree and recreate parent-child relationships
         after they are imported
        """
        if self.content():
            parent = Page.objects.get(id=parent_id)

            # Save the selected section page
            response = requests.get(
                self._base_url + API_PAGES_ENDPOINT + str(indexes[0]) + "/"
            )

            section_page = response.json()
            self.process_child_section(section_page["id"], parent)


class RecordKeeper(object):
    def __init__(self):
        # maps foreign IDs to local IDs
        # used when a new item is created
        self.foreign_local_map = {
            "page_map": {},
            "image_map": {},
        }

        # maps local id to list of foreign page ids
        # used when a foreign item is referenced
        self.foreign_to_many_foreign_map = {
            "recommended_articles": {},
            "related_sections": {},
            "nav_tags": {},
            "section_tags": {},
            "reaction_questions": {},
        }

        # maps local page to foreign id
        self.foreign_to_foreign_map = {
            "banner_link_page": {}
        }

    def record_relation(self, id_map_key, foreign_page_id, local_page_id):
        record = self.foreign_local_map[id_map_key]
        if (foreign_page_id in record and
                record[foreign_page_id] != local_page_id):
            raise RecordOverwriteError("RecordOverwriteError", None)
        else:
            record[foreign_page_id] = local_page_id

    def get_local(self, id_map_key, foreign_page_id):
        record = self.foreign_local_map[id_map_key]
        if foreign_page_id in record:
            return record[foreign_page_id]
        else:
            raise ReferenceUnimportedContent(
                "ReferenceUnimportedContent",
                None)

    def record_foreign_relations(self, field, related_item_key, id_map_key,
                                 nested_fields, page_id):
        record_keeper = self.foreign_to_many_foreign_map[id_map_key]
        if ((field in nested_fields) and nested_fields[field]):
            relationship_object_list = nested_fields[field]

            # Assumption: this item is only processed once
            # TODO: create override checks
            record_keeper[page_id] = []

            for relationship_object in relationship_object_list:
                if related_item_key in relationship_object:
                    related_item = relationship_object[related_item_key]
                    if "id" in related_item:
                        foreign_id = related_item["id"]
                        record_keeper[page_id].append(foreign_id)
                    else:
                        raise Exception(
                            ("key of 'id' does not exist in related_item"
                             " of type: {}").format(related_item_key))
                else:
                    raise Exception(
                        ("key of '{}' does not exist in nested_field"
                         " of type: {}").format(related_item_key, field))

    def record_page_relation(self, foreign_page_id, local_page_id):
        self.record_relation("page_map", foreign_page_id, local_page_id)

    def record_image_relation(self, foreign_page_id, local_page_id):
        self.record_relation("image_map", foreign_page_id, local_page_id)

    def get_local_page(self, foreign_page_id):
        return self.get_local("page_map", foreign_page_id)

    def get_local_image(self, foreign_page_id):
        return self.get_local("image_map", foreign_page_id)

    def record_recommended_articles(self, nested_fields, page_id):
        self.record_foreign_relations(
            "recommended_articles", "recommended_article",
            "recommended_articles", nested_fields, page_id)

    def record_related_sections(self, nested_fields, page_id):
        self.record_foreign_relations(
            "related_sections", "section",
            "related_sections", nested_fields, page_id)

    def record_section_tags(self, nested_fields, page_id):
        self.record_foreign_relations(
            "section_tags", "tag",
            "section_tags", nested_fields, page_id)

    def record_nav_tags(self, nested_fields, page_id):
        self.record_foreign_relations(
            "nav_tags", "tag",
            "nav_tags", nested_fields, page_id)

    def record_reaction_questions(self, nested_fields, page_id):
        self.record_foreign_relations(
            "reaction_questions", "reaction_question",
            "reaction_questions", nested_fields, page_id)

    def record_banner_page_link(self, nested_fields, page_id):
        field = "banner_link_page"
        id_map_key = "banner_link_page"
        record_keeper = self.foreign_to_foreign_map[id_map_key]
        if ((field in nested_fields) and nested_fields[field]):
            relationship_object = nested_fields[field]
            record_keeper[page_id] = relationship_object["id"]


class BaseImporter(object):
    def __init__(self, site_pk, base_url, record_keeper=None):
        # TODO: handle case where base_url is not valid
        self.base_url = self.format_base_url(base_url)
        self.api_url = '{}/api/v2/'.format(self.base_url)
        self.site_pk = site_pk
        self.language_setting, created = Languages.objects.get_or_create(
            site_id=self.site_pk)
        self.record_keeper = record_keeper

    def format_base_url(self, base_url):
        if base_url[-1] == '/':
            return base_url[:-1]
        else:
            return base_url


class ImageImporter(BaseImporter):
    def __init__(self, site_pk, base_url, record_keeper=None):
        super(ImageImporter, self).__init__(site_pk, base_url,
                                            record_keeper=record_keeper)
        self.image_url = "{}images/".format(self.api_url)
        self.image_hashes = {}
        self.image_widths = {}
        self.image_heights = {}
        self.get_image_details()

    def get_image_details(self):
        '''
        Create a reference of site images by hash, width and height
        '''
        if Image.objects.count() == 0:
            return None

        for local_image in Image.objects.all():
            self.image_hashes[get_image_hash(local_image)] = local_image

            if local_image.width in self.image_widths:
                self.image_widths[local_image.width].append(local_image)
            else:
                self.image_widths[local_image.width] = [local_image]

            if local_image.height in self.image_heights:
                self.image_heights[local_image.height].append(local_image)
            else:
                self.image_heights[local_image.height] = [local_image]

    def get_replica_image(self, width, height, img_hash):
        if width in self.image_widths:
                possible_matches = self.image_widths[width]
                if height in self.image_heights:
                    possible_matches = list(
                        set(self.image_heights[height] +
                            possible_matches))
                    if (img_hash in self.image_hashes and
                            self.image_hashes[img_hash] in possible_matches):
                        matching_image = self.image_hashes[img_hash]
                        return matching_image
        return None

    def import_image(self, image_id):
        '''
        Imports and returns image

        Input: foreign image ID

        Attempts to avoid duplicates by matching image titles.
        If a match is found it refers to local instance instead.
        If it is not, the image is fetched, created and referenced.
        '''
        image_detail_url = "{}{}/".format(self.image_url, image_id)
        img_response = requests.get(image_detail_url)
        img_info = json.loads(img_response.content)

        if img_info["image_hash"] is None:
            raise ValueError('image hash should not be none')

        # check if a replica exists
        local_image = self.get_replica_image(
            img_info["width"],
            img_info["height"],
            img_info["image_hash"])
        if local_image:
            # update record keeper
            if self.record_keeper:
                self.record_keeper.record_image_relation(
                    img_info["id"],
                    local_image.id)
            # TODO: update logs
            return local_image
        else:
            # use the local title of the image
            new_image = self.fetch_and_create_image(
                img_info['image_url'],
                img_info["title"])

            # update record keeper
            if self.record_keeper:
                self.record_keeper.record_image_relation(
                    img_info["id"],
                    new_image.id)
            # TODO: update logs
            return new_image

    def import_images(self):
        '''
        Fetches all images from site
        '''
        images = list_of_objects_from_api(self.image_url)

        if not images:
            return None

        # iterate through foreign images
        for image_summary in images:
            self.import_image(image_summary["id"])

    def fetch_and_create_image(self, relative_url, image_title):
        '''
        fetches, creates and return image object
        '''
        # TODO: handle image unavailable
        image_media_url = "{}{}".format(self.base_url, relative_url)
        image_file = requests.get(image_media_url)
        local_image = Image(
            title=image_title,
            file=ImageFile(
                BytesIO(image_file.content), name=image_title
            )
        )
        local_image.save()
        return local_image


class LanguageImporter(BaseImporter):
    def __init__(self, site_pk, base_url, record_keeper=None):
        super(LanguageImporter, self).__init__(site_pk, base_url,
                                               record_keeper=record_keeper)
        self.language_url = "{}languages/".format(self.api_url)

    def get_language_ids(self):
        '''
        Return list of foreign language IDs from API language endpoint

        TODO: add in validation before creating languages
        '''
        languages = list_of_objects_from_api(self.language_url)

        language_ids = []
        for language in languages:
            language_ids.append(language["id"])
        return language_ids

    def copy_site_languages(self):
        language_foreign_ids = self.get_language_ids()
        language_setting, created = Languages.objects.get_or_create(
            site_id=self.site_pk)
        for foreign_id in language_foreign_ids:
            language_url = "{}{}/".format(self.language_url,
                                          foreign_id)
            response = requests.get(language_url)
            content = json.loads(response.content)

            sle, created = SiteLanguageRelation.objects.get_or_create(
                locale=content['locale'],
                is_active=content['is_active'],
                language_setting=language_setting)




class ContentImporter(BaseImporter):
    def recreate_relationships(self, class_, attribute_name, key):

        iterable = self.record_keeper.foreign_to_many_foreign_map[key]
        for foreign_page_id, foreign_page_id_list in iterable.iteritems():

            # Assumption: local page has been indexed and exists
            # TODO: handle case where it doesn't exist
            local_page_id = self.record_keeper.get_local_page(foreign_page_id)
            local_page = Page.objects.get(id=local_page_id).specific

            for foreign_page_id in foreign_page_id_list:
                try:
                    local_version_page_id = self.record_keeper.get_local_page(foreign_page_id)    # noqa
                    foreign_page = Page.objects.get(id=local_version_page_id).specific
                    realtionship_object = class_(page=local_page)
                    setattr(realtionship_object, attribute_name, foreign_page)
                    realtionship_object.save()
                except ReferenceUnimportedContent as e:
                    print(e)

    def __init__(self, site_pk, base_url, record_keeper=None):
        super(ContentImporter, self).__init__(site_pk, base_url,
                                              record_keeper=record_keeper)

    def create_recommended_articles(self):
        self.recreate_relationships(
            ArticlePageRecommendedSections,
            'recommended_article',
            'recommended_articles',
        )
    def create_related_sections(self):
        self.recreate_relationships(
            ArticlePageRelatedSections,
            'section',
            'related_sections',
        )
    def create_nav_tag_relationships(self):
        self.recreate_relationships(
            ArticlePageTags,
            'tag',
            'nav_tags'
        )
    def create_section_tag_relationship(self):
        self.recreate_relationships(
            SectionPageTags,
            'tag',
            'section_tags'
        )

    def get_foreign_page_id_from_type(self, page_type):
        '''
        Get the foreign page id based on type

        Only works for index pages
        '''
        response = requests.get("{}pages/?type={}".format(
            self.api_url, page_type))
        content = json.loads(response.content)
        return content["items"][0]["id"]

    def attach_page(self, parent, content):
        page_type = content["meta"]["type"].split(".")[-1]
        class_ = eval(page_type)
        content_copy = dict(content)

        if not issubclass(class_, ImportableMixin):
            # TODO: log this
            return None

        # TODO: make a copy of the record_keeper class

        try:
            page = class_.create_page(
                content_copy, class_, record_keeper=self.record_keeper)
        except Exception as e:
            # avoid side-effects of adding the page
            # TODO: restore copy of record Keeper class
            # TODO: Log exceptions surface from creating page
            return None

        try:
            parent.add_child(instance=page)
            parent.save_revision().publish()
            page.save_revision().publish()
        except Exception as e:
            # TODO: log failed page save and details
            return None

        self.record_keeper.record_page_relation(
            content["id"],
            page.id
        )
        # TODO: Log successful import
        return page

    def attach_translated_content(self, local_main_lang_page,
                                  content, locale):
        '''
        Wrapper for  attach_page

        Creates the content
        Then attaches a language relation from the main language page to the
        newly created Page
        Note: we get the parent from the main language page
        '''
        try:
            page = self.attach_page(
                local_main_lang_page.get_parent(),
                content)
        except:
            # TODO: log this
            return None

        try:
            # create the translation object for page
            language = SiteLanguageRelation.objects.get(
                language_setting=self.language_setting,
                locale=locale)
            language_relation = page.languages.first()
            language_relation.language = language
            language_relation.save()
            PageTranslation.objects.get_or_create(
                page=local_main_lang_page,
                translated_page=page)
        except:
            # TODO: log that creating translation failed
            # TODO: log that page is now being deleted
            page.delete()
        return page

    def copy_page_and_children(self, foreign_id, parent_id):
        '''
        Recusively copies over pages, their translations, and child pages
        '''
        url = "{}/api/v2/pages/{}/".format(self.base_url, foreign_id)

        # TODO: create a robust wrapper around this functionality
        response = requests.get(url)
        try:
            content = json.loads(response.content)
        except Exception as e:
            return None

        parent = Page.objects.get(id=parent_id).specific
        page = None
        try:
            page = self.attach_page(parent, content)
        except Exception as e:
            # TODO: log this
            return None

        if page:
            # create translations
            if content["meta"]["translations"]:
                for translation_obj in content["meta"]["translations"]:
                    _url = "{}/api/v2/pages/{}/".format(self.base_url,
                                                        translation_obj["id"])
                    # TODO: create a robust wrapper around this functionality
                    _response = requests.get(_url)
                    if _response.content:
                        _content = json.loads(_response.content)

                        self.attach_translated_content(
                            page, _content, translation_obj["locale"])
                    else:
                        # TODO: log this
                        pass

            main_language_child_ids = content["meta"]["main_language_children"]

            # recursively iterate through child nodes
            if main_language_child_ids:
                for main_language_child_id in main_language_child_ids:
                    self.copy_page_and_children(
                        foreign_id=main_language_child_id,
                        parent_id=page.id)

    def copy_children(self, foreign_id, existing_node):
        '''
        Initiates copying of tree, with existing_node acting as root
        '''
        url = "{}/api/v2/pages/{}/".format(self.base_url, foreign_id)

        # TODO: create a robust wrapper around this functionality
        response = requests.get(url)
        content = json.loads(response.content)

        main_language_child_ids = content["meta"]["main_language_children"]
        for main_language_child_id in main_language_child_ids:
                self.copy_page_and_children(foreign_id=main_language_child_id,
                                            parent_id=existing_node.id)

    def create_banner_page_links(self):
        for banner_page_id, linked_page_foreign_id in self.record_keeper.banner_page_links.iteritems():  # noqa
            banner = BannerPage.objects.get(id=banner_page_id)
            local_id = self.record_keeper.get_local_page(linked_page_foreign_id)
            linked_page = Page.objects.get(id=local_id).specific
            banner.banner_link_page = linked_page
            banner.save_revision().publish()

    def restore_relationships(self):
        pass
