# -*- coding: utf-8 -*-

from src.services.mongodb.feeds_service import FeedService
from src.sentinews.crawler import Crawler
from src.sentinews.feeds import Feed
from src.services.mongodb.connector import MongoConnector
from datetime import datetime

''' This class also builds and inserts into DB.
    DB structure:
      Table feed_sources: id and url of all feeds from where to read the news.
      Table original_news_entries: title, text and url of all news read.
'''


class NewsCrawler(object):
    def __init__(self):
        self.service = FeedService()
        self._cursor_start()

    def _cursor_start(self):
        db = MongoConnector.get_instance()
        if db['system']['namespaces'].find({'name': 'sentinews.feeds'}).count() == 0:
            self.service.save(Feed('cnn_spanish', 'http://cnnespanol.cnn.com/feed/',
                                   'cnn_parser.CNNParser',datetime.utcnow()))
            self.service.save(Feed('euronews', 'http://feeds.feedburner.com/euronews/es/news?format=xml',
                                   'euronews_parser.EuroNewsParser',datetime.utcnow()))
            self.service.save(Feed('elpais', 'http://ep00.epimg.net/rss/elpais/portada_america.xml',
                                   'elpais_parser.ElPaisParser',datetime.utcnow()))
            self.service.save(Feed('bbc', 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['america']))

    def crawl_all(self):
      entries = []
      crawler = Crawler()
      for feed in self.service.get_all():
          print feed
          news_entries = crawler.crawl(feed.parser, feed.url[0][0], feed.default_tags)
          entries.extend(news_entries)
      return entries
