# -*- coding: utf-8 -*-

import sqlite3
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
from src.sentinews.news_crawler.euronews_crawler import EuroNewsCrawler
from src.sentinews.news_crawler.elpais_crawler import ElPaisCrawler

''' This class also builds and inserts into DB.
    DB structure:
      Table feed_sources: id and url of all feeds from where to read the news.
      Table original_news_entries: title, text and url of all news read.
'''


class NewsCrawler(object):

  def __init__(self):
    self.connection = sqlite3.connect("news_crawler.db")
    self.connection.text_factory = str
    self.cursor = self.connection.cursor()
    self._cursor_start()
    self.crawlers_by_id = {
        "cnn_spanish": CNNCrawler, "euronews": EuroNewsCrawler,
        "elpais": ElPaisCrawler}

  def _cursor_start(self):
    self.cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='feed_sources'")
    if not self.cursor.fetchall():
        self.cursor.execute(
            "CREATE TABLE feed_sources (id text, url text, last_updated date)")
        self.cursor.execute(
            "INSERT INTO feed_sources VALUES ('cnn_spanish', 'http://cnnespanol.cnn.com/feed/', NULL)")
        self.connection.commit()
    self.cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='original_news_entries'")
    if not self.cursor.fetchall():
        self.cursor.execute(
            "CREATE TABLE original_news_entries (title text, content text, url text, tags text)")
        self.connection.commit()

  def crawl_all(self):
    self.cursor.execute("SELECT * FROM feed_sources")
    entries = []
    for _id, url, last_updated in self.cursor.fetchall():
        print _id
        crawler = self.crawlers_by_id[_id]()
        print crawler
        news_entries = crawler.crawl()
        for entry in news_entries:
          self.cursor.execute('INSERT INTO original_news_entries VALUES (?, ?, ?, ?)' , (entry.title, 
                                                                                       entry.content, 
                                                                                       entry.source,
                                                                                       "|".join(entry.tags)))
        entries.extend(news_entries)
    
    self.connection.commit()
    self.connection.close()

    return entries
