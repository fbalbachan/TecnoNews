import ConfigParser
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.parsers import *
import feedparser


class Crawler(object):

    def _filter_entries(self, entries):
        ''' Filter entries that already exist in the DB,
            we dont want to parse them again. '''
        service = NewsEntriesService()
        # Filter if we already process the url
        # and if is not in sections we want to filter
        return [entry for entry in entries
                if len(service.get_list({'url': unicode(entry.link)})) == 0
                and not '/videos/' in entry.link
                and not '/inenglish/' in entry.link
                and not '/album/' in entry.link
                and not '/video_fotos/' in entry.link]


    def _filter_by_tag(self, news_entries):
        Config = ConfigParser.ConfigParser()
        Config.read("config")

        tags_filename = Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tagsfile:
            tags = [tag.strip().lower() for tag in tagsfile]
        return [entry for entry in news_entries if len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]

    def create_parser(self, cls_parser):
        return cls_parser()

    def crawl(self, cls_parser, url, default_tags=None):
        parser = self.create_parser(eval(cls_parser))
        news_entries = []
        parsed_feeds = feedparser.parse(url)
        filtered_entries = self._filter_entries(parsed_feeds["entries"])
        for entry in filtered_entries:
            if default_tags is not None:
                news_entry = parser.parse(entry["link"], default_tags)    
            else:
                news_entry = parser.parse(entry["link"])
                
            news_entries.append(news_entry)
        filtered_by_tags = self._filter_by_tag(news_entries)
        return filtered_by_tags