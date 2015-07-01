__author__ = 'Pablo Perez De Angelis'

from src.utils.languageFilter import LanguageFilter
from src.utils.sanitizer import Sanitizer
from src.utils.bit_opener import BitOpener
from src.utils.logger_utils import get_crawler_logger
from src.sentinews.news_entry import NewsEntry
import traceback

logger = get_crawler_logger()


class GenericParser(object):
    def __init__(self):
        self.language_filter = LanguageFilter()
        self.sanitizer = Sanitizer()
        self.opener = BitOpener()

    def sanitize(self, content):
        return self.sanitizer.process_content(content=content)

    def create_news_entry(self, title, content, tags, source, url, categories,
                          image_search_string=None):
        new_entry = None
        content = self.sanitize(content)
        assert content.find('function()') == -1

        if categories and u'video' in categories:
            return None

        if len(tags) or categories:
            try:
                new_entry = NewsEntry(title=title, content=content,
                                      tags=tags,
                                      source=source,
                                      url=url,
                                      original_categories=categories,
                                      image_search_string=image_search_string)

            except Exception as e:
                logger.error("%s" % e.message)
                logger.error(traceback.format_exc())

        if not new_entry:
            logger.error(u"Couldn't parse news in elmundo ")
            logger.error(u"Url: %s " % url)

        return new_entry