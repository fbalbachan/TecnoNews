# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
import datetime
from src.sentinews.news_crawler.cnn_parser import CNNParser
import wikipedia as wk
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler

''' Clase para testear una sola noticia end to end '''

link = "http://cnnespanol.cnn.com/2014/09/19/vive-el-golf-consejos-de-golf-de-rafael-alarcon-como-mover-la-pelota/"

parser = CNNParser()
news_entry = parser.parse(link)
CNNCrawler()
c = NewsRewriter(news_entry)
c.rewrite()
c.publish()