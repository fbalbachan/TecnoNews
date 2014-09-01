# -*- coding: utf-8 -*-

import sqlite3
from cnn_crawler import CNNCrawler

connection = sqlite3.connect("news_crawler.db")
cursor = connection.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feed_sources'")
if not cursor.fetchall():
    #cursor.execute("CREATE TABLE news (source_id text, url text, last_updated date, text text)")
    cursor.execute("CREATE TABLE feed_sources (id text, url text, last_updated date)")
    cursor.execute("INSERT INTO feed_sources VALUES ('cnn_spanish', 'http://cnnespanol.cnn.com/feed/', NULL)")
    connection.commit()

crawlers_by_id = { "cnn_spanish" : CNNCrawler }

cursor.execute("SELECT * FROM feed_sources")
for _id, url, last_updated in  cursor.fetchall():
    crawler = crawlers_by_id[_id](url)
    news = crawler.crawl()

connection.close()