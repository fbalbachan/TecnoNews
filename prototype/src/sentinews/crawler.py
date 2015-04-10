# -*- coding: utf-8 -*-

import ConfigParser
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.parsers import *
from src.utils.logger_utils import get_crawler_logger
import feedparser
from src.utils.sanitizer import Sanitizer
from src.utils.configProvider import ConfigProvider
import traceback

crawler_logger = get_crawler_logger()


class Crawler(object):

    def __init__(self):
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
                and not '/video_fotos/' in entry.link
                and not u'#As\xedLoVivimos' in entry.title
                and not u'Resumen' in entry.title
                and not u'CNN' in entry.title]

    def _filter_by_tag(self, news_entries):
        Config = ConfigProvider()

        tags_filename = Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tags_file:
            tags = [unicode(tag.strip().lower(), 'utf-8') for tag in tags_file]
        return [entry for entry in news_entries if len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]

    def create_parser(self, cls_parser):
        return cls_parser()

    def crawl(self, cls_parser, url, default_tags=None, max_number_to_parse=5):
        crawler_logger.info("Start parser %s" % cls_parser)
        crawler_logger.info("Parsing url %s" % url)

        parser = self.create_parser(eval(cls_parser))
        news_entries = []
        parsed_feeds = feedparser.parse(url)

        filtered_entries = self._filter_entries(parsed_feeds["entries"])
        filtered_entries = filtered_entries[:max_number_to_parse]

        for idx, feedParserDict in enumerate(filtered_entries):
            crawler_logger.info("processing %s of %s" % (idx, len(filtered_entries)))
            crawler_logger.info("entry url: %s" % feedParserDict["link"])
            try:
                # TODO: simplify this making parse.parse accept degault_tags as None
                if default_tags:
                    news_entry = parser.parse(feedParserDict["link"], default_tags)
                else:
                    news_entry = parser.parse(feedParserDict["link"])

                if news_entry:
                    news_entry.content = self.sanitizer.process_content(news_entry.content)
                    news_entries.append(news_entry)

            except Exception as e:
                crawler_logger.error("<crawler> <crawl> %s" % feedParserDict["link"])
                crawler_logger.error(traceback.format_exc())
                crawler_logger.error("%s" % e.message)

        filtered_by_tags = self._filter_by_tag(news_entries)

        crawler_logger.info("filtered %s " % [x.title for x in filtered_entries])
        crawler_logger.info("Ends parser %s" % cls_parser)
        return filtered_by_tags