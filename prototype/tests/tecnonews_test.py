# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
import datetime
from src.sentinews.news_crawler.cnn_parser import CNNParser

''' Clase para testear una sola noticia end to end '''

link = "http://cnnespanol.cnn.com/2014/09/16/microsoft-presentara-windows-9-el-30-de-septiembre/"

parser = CNNParser()
news_entry = parser.parse(link)
c = NewsRewriter(news_entry)
c.rewrite()
c.publish()