#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *


class CNNParser:
    source = u"CNN en español"
    def parse(self, url, limit=1):
        soup = BeautifulSoup(urlopen(url).read())
        articles = soup.findAll('div' , { "class" : "cnnRightPost" }, limit=limit)
        new_entries = []
        for article in articles:
            title = article.find('h1').text
            content = self._remove_cnn_header(article.find('div').text)

            try:
              tags = article.find('span', class_ = "cnnBlogFiledBy cnn_categories").text[11:].split(u"\xa0\u2022\xa0")
            except:
              logger = get_logger('tecnonews')
              logger.info('Tags not found: %s' %(article.find('span', class_ = "cnnBlogFiledBy cnn_categories")))
              tags = []

            if (content.find('function()') == -1):
                new_entries.append(NewsEntry(title, content, tags, self.source)) 
        return new_entries[0] if len(new_entries) > 0 else NewsEntry('','',[],'')

        
    def _remove_cnn_header(self, text):
        dashes = [u'\u2014', u'\u2013', '-']

        text_with_dash = text[:100]
        positions = [(dash,text_with_dash.find(dash)) for dash in dashes if text_with_dash.find(dash) > -1]

        min_pos = 9999
        min_dash = None
        for dash, pos in positions:
            if pos < min_pos:
                min_pos = pos
                min_dash = dash

        if min_dash:
            text_without_dash = text_with_dash.split(min_dash)[1][1:]
            text = text_without_dash + text[100:]
        
        return text        
