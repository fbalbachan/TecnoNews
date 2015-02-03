import ConfigParser
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.parsers import *
import feedparser
from src.utils.sanitize import Sanitizer

crawler_logger = None


class Crawler(object):

    def __init__(self):
        self.get_logger()
        self.sanitizer = Sanitizer()

    def _filter_entries(self, entries):
        ''' Filter entries that already exist in the DB,
            we dont want to parse them again. '''
        service = NewsEntriesService()
        # Filter if we already process the url
        # and if is not in sections we want to filter

        return [entry for entry in entries if len(service.get_list({'url': unicode(entry.link)})) == 0
                and not '/videos/' in entry.link
                and not '/inenglish/' in entry.link
                and not '/album/' in entry.link
                and not '/video_fotos/' in entry.link]

    def _filter_by_tag(self, news_entries):
        Config = ConfigParser.ConfigParser()
        Config.read("config")

        tags_filename = Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tags_file:
            tags = [unicode(tag.strip().lower(), 'utf-8') for tag in tags_file]
        return [entry for entry in news_entries if len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]

    def create_parser(self, cls_parser):
        return cls_parser()

    def crawl(self, cls_parser, url, default_tags=None):
        crawler_logger.info("Start parser %s" % cls_parser)
        crawler_logger.info("Parsing url %s" % url)

        parser = self.create_parser(eval(cls_parser))
        news_entries = []
        parsed_feeds = feedparser.parse(url)

        filtered_entries = self._filter_entries(parsed_feeds["entries"])

        for idx, entry in enumerate(filtered_entries):
            crawler_logger.info("processing %s of %s" % (idx, len(filtered_entries)))
            # TODO: simplify this making parse.parse accept degault_tags as None
            if default_tags is not None:
                news_entry = parser.parse(entry["link"], default_tags)    
            else:
                news_entry = parser.parse(entry["link"])

            if news_entry is not None: 
                news_entry.content = self.sanitizer.process_content(news_entry.content)
                news_entries.append(news_entry)

        filtered_by_tags = self._filter_by_tag(news_entries)

        crawler_logger.info("Ends parser %s" % cls_parser)
        return filtered_by_tags

    @staticmethod
    def get_logger():
        global crawler_logger
        if not crawler_logger:
            import logging
            from logging.handlers import RotatingFileHandler
            import logging.handlers

            logging.basicConfig(level=logging.INFO, format='%(message)s')

            logger = logging.getLogger('Crawler')
            logger.addHandler(RotatingFileHandler('logs/crawlers.log', 'a',
                maxBytes=5000000, backupCount=50))
            logger.addHandler(logging.StreamHandler())
            logger.propagate = False
            crawler_logger = logger
        return crawler_logger
