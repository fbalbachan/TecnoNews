# -*- coding: utf-8 -*-

from src.services.mongodb.feeds_service import FeedService
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
from src.sentinews.news_crawler.euronews_crawler import EuroNewsCrawler
from src.sentinews.news_crawler.elpais_crawler import ElPaisCrawler
from src.sentinews.feeds import Feed
from datetime import datetime

''' This class also builds and inserts into DB.
    DB structure:
      Table feed_sources: id and url of all feeds from where to read the news.
      Table original_news_entries: title, text and url of all news read.
'''


class NewsCrawler(object):

  def __init__(self):
    self.service = FeedService
    self._cursor_start()
    self.crawlers_by_id = {
        "cnn_spanish": CNNCrawler, "euronews": EuroNewsCrawler,
        "elpais": ElPaisCrawler}

  def _cursor_start(self):
    if self.db['system']['namespace'].find({'name': 'sentinews.feeds'}).count() > 1:
      
      self.service.save(Feed('cnn_spanish', 'http://cnnespanol.cnn.com/feed/',
        datetime.utcnow()).to_dict())
      self.service.save(Feed('euronews', 'http://es.euronews.com/noticias/boletin/',
        datetime.utcnow()).to_dict())
      self.service.save(Feed('elpais','http://elpais.com/tag/fecha/hoy',
        datetime.utcnow()).to_dict())

  def crawl_all(self):
    entries = []
    if entries is not None and len(entries) > 0:
      for feed in self.service.get_all():
          print feed.id
          crawler = self.crawlers_by_id[_id]()
          print crawler
          news_entries = crawler.crawl()
          entries.extend(news_entries)
    return entries
