# -*- coding: utf-8 -*-

import feedparser
from re import search
import sqlite3
import ConfigParser
from src.services.mongodb.news_entries_service import NewsEntriesService

from src.sentinews.news_crawler.cnn_parser import CNNParser

FEED_URL = "http://cnnespanol.cnn.com/feed/"


class CNNCrawler:
    def __init__(self):
        self.feed = feedparser.parse(FEED_URL)

    def crawl(self):
        parser = CNNParser()
        news_entries = []
        filtered_entries = self._filter_entries(self.feed["entries"])
        for entry in filtered_entries:
            news_entry = parser.parse(entry["link"])
            news_entries.append(news_entry)
        filtered_by_tags = self._filter_by_tag(news_entries)
        return filtered_by_tags


    def _filter_entries(self, entries):
        ''' Filter entries that already exist in the DB,
            we dont want to parse them again. '''
        service = NewsEntriesService()
        list_entries = [entry for entry in entries 
            if len(service.get_list({'url': unicode(entry.link)})) == 0]
        return list_entries

    def _filter_by_tag(self, news_entries):
        Config = ConfigParser.ConfigParser()
        Config.read("config")

        tags_filename =  Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tagsfile:
            tags = [tag.strip().lower() for tag in tagsfile]
        return [entry for entry in news_entries if  len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]
