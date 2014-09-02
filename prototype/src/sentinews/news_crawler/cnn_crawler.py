# -*- coding: utf-8 -*-

import feedparser
from re import search

from src.sentinews.news_crawler.cnn_parser import CNNParser

FEED_URL = "http://cnnespanol.cnn.com/feed/"


class CNNCrawler:
    def __init__(self):
        self.feed = feedparser.parse(FEED_URL)

    def crawl(self):
        parser = CNNParser()
        news_entries = []

        for entry in self.feed["entries"]:
            news_entry = parser.parse(entry["link"])
            news_entries.append(news_entry)

        return news_entries




