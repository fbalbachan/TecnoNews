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
            self.service.save(Feed('elpais', 'http://ep00.epimg.net/rss/tags/ultimas_noticias.xml',
                                   'elpais_parser.ElPaisParser',datetime.utcnow()))
            self.service.save(Feed('elpais_america', 'http://ep00.epimg.net/rss/tags/ultimas_noticias.xml',
                                   'elpais_parser.ElPaisParser',datetime.utcnow()))
            self.service.save(Feed('bbc_america', 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['america']))
            self.service.save(Feed('bbc_internacional', 'http://www.bbc.co.uk/mundo/temas/internacional/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['america']))
            self.service.save(Feed('bbc_economia', 'http://www.bbc.co.uk/mundo/temas/economia/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['economia']))
            self.service.save(Feed('bbc_tecnologia', 'http://www.bbc.co.uk/mundo/temas/tecnologia/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['tecnologia']))
            self.service.save(Feed('bbc_ciencia', 'http://www.bbc.co.uk/mundo/temas/ciencia/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['ciencia']))
            self.service.save(Feed('bbc_salud', 'http://www.bbc.co.uk/mundo/temas/salud/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['salud']))
            self.service.save(Feed('bbc_cultura', 'http://www.bbc.co.uk/mundo/temas/cultura/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['sociedad']))
            self.service.save(Feed('bbc_deportes', 'http://www.bbc.co.uk/mundo/temas/deportes/index.xml',
                                   'bbc_parser.BBCParser',datetime.utcnow(),['deportes']))

    def crawl_all(self):
      entries = []
      crawler = Crawler()
      for feed in self.service.get_all():
          print feed
          news_entries = crawler.crawl(feed.parser, feed.url[0][0], feed.default_tags)
          entries.extend(news_entries)

      return self.__clean_duplicated(entries)

    def __clean_duplicated(self, entries):
        cleaned_entries = []
        cleaned_entries_urls = []

        for entry in entries:
            if entry.url not in cleaned_entries_urls:
                cleaned_entries.append(entry)
                cleaned_entries_urls.append(entry.url)

        return cleaned_entries
