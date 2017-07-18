from .constants import (
    AVAILABLE_ARTICLES,
    AVAILABLE_SECTIONS,
    AVAILABLE_SECTION_CHILDREN,
    RELATED_IMAGE,
    ARTICLE_PAGE_RESPONSE,
    SECTION_PAGE_RESPONSE,
)


# Inspired by http://stackoverflow.com/a/28507806
def mocked_requests_get(url, *args, **kwargs):
    """ This object will be used to mock requests.get() """
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def content(self):
            return self.content

        def json(self):
            return self.content

    if url == "http://localhost:8000/api/v2/pages/":
        return MockResponse(AVAILABLE_ARTICLES, 200)
    elif url == "http://localhost:8000/api/v2/images/1/":
        return MockResponse(RELATED_IMAGE, 200)
    elif url == "http://localhost:8000/api/v2/pages/?child_of=2":
        return MockResponse(AVAILABLE_SECTION_CHILDREN, 200)
    # Responses for individual section page requests
    elif url == "http://localhost:8000/api/v2/pages/2/":
        return MockResponse(AVAILABLE_SECTIONS["items"][0], 200)
    elif url == "http://localhost:8000/api/v2/pages/3/":
        return MockResponse(AVAILABLE_SECTIONS["items"][1], 200)
    elif url == "http://localhost:8000/api/v2/pages/4/":
        return MockResponse(AVAILABLE_SECTIONS["items"][2], 200)

    # Responses for individual article page requests
    elif url == "http://localhost:8000/api/v2/pages/10/":
        return MockResponse(AVAILABLE_ARTICLES["items"][0], 200)
    elif url == "http://localhost:8000/api/v2/pages/11/":
        return MockResponse(AVAILABLE_ARTICLES["items"][1], 200)
    elif url == "http://localhost:8000/api/v2/pages/12/":
        return MockResponse(AVAILABLE_ARTICLES["items"][2], 200)
    elif url == "http://localhost:8000/api/v2/pages/?type=core.ArticlePage" \
                "&fields=title,subtitle,body,tags,commenting_state," \
                "commenting_open_time,commenting_close_time," \
                "social_media_title,social_media_description," \
                "social_media_image,related_sections," \
                "featured_in_latest,featured_in_latest_start_date" \
                ",featured_in_latest_end_date,featured_in_section," \
                "featured_in_section_start_date," \
                "featured_in_section_end_date" \
                ",featured_in_homepage,featured_in_homepage_start_date" \
                ",featured_in_homepage_end_date,feature_as_topic_of_the_day" \
                ",promote_date,demote_date,metadata_tags," \
                "latest_revision_created_at," \
                "image,social_media_image,social_media_description," \
                "social_media_title&order=latest_revision_created_at":
        return MockResponse(AVAILABLE_ARTICLES, 200)

    return MockResponse({}, 404)


def fake_article_page_response(**kwargs):
    '''
    Returns a fully featured article with all the
    bells and whistles.

    Pass in kwargs to suppress certain elements
    '''
    response = ARTICLE_PAGE_RESPONSE
    response.update(kwargs)
    return response


def fake_section_page_response(**kwargs):
    '''
    Returns a fully featured article with all the
    bells and whistles.

    Pass in kwargs to suppress certain elements
    '''
    response = SECTION_PAGE_RESPONSE
    response.update(kwargs)
    return response
