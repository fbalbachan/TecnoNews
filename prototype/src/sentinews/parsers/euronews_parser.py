#!/usr/bin/python
# -*- coding: utf-8 -*-
from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *
from src.utils.languageFilter import LanguageFilter
from ConfigParser import ConfigParser


class EuroNewsParser(object):
    def __init__(self):
        self.language_filter = LanguageFilter()
        config = ConfigParser()
        config.read('config')
        self.language_filter_status = config.get('language_filter', 'status')

    base_path = 'http://es.euronews.com'
    source = u'Euronews'

    def parse(self, url):
        soup = BeautifulSoup(urlopen(url).read())
        paragraphs =  None
        tags = []
        title = ''
        if soup is not None:
            try:
                paragraphs = soup.find('div', {'id': 'articleTranscript'}).find_all('p')
            except Exception, e:
                logger = get_logger('tecnonews')
                logger.error("Problem Parsing euronews new..")

            if paragraphs is not None:
                content_paragraphs_list = [paragraph.text for paragraph in paragraphs]
            else:
                content_paragraphs_list = []
                    
            content_str = [ text + '\n' for text in content_paragraphs_list]
            tags = []
            if paragraphs is not None:
                ul_tags = soup.find('ul', {'class': 'kwl'})
                if not ul_tags is None: 
                    li_tags = soup.find('ul', {'class': 'kwl'}).find_all('li')
                    tags = [tag.find('a').text for tag in li_tags]
            content = " ".join(content_str)
        else:
            content = ''
        
        title_obj = soup.find(
            'div', {'id': 'title-wrap-new'}).find('h1').find('a')

        if title_obj is not None:
            title = title_obj.text
        
        if self.language_filter_status == 'ON':
            content = self.language_filter.only_spanish_paragraph(content)
        
        
        return NewsEntry(title, content, tags, self.source, url=url) \
            if len(content) > 1  and len(tags) > 0 and len(title) > 0 else None
