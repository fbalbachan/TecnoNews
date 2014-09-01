# -*- coding: utf-8 -*-

import feedparser
from re import search

from cnn_parser import CNNParser


class CNNCrawler:
    def __init__(self, feed_url):
        self.feed = feedparser.parse(feed_url)

    def crawl(self):
        parser = ClarinParser()
        news = []

        for entry in self.feed["entries"]:
            _id = entry["id"]
            if search("/(mundo|sociedad)/", _id):
                text = parser.parse(entry["link"])
                print (entry["title"], entry["id"], entry["updated"], text)
                news.append((entry["title"], entry["id"], entry["updated"], text))

        return news
