#!/usr/bin/python
# -*- coding: utf-8 -*-
from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from src.utils.logger_utils import *
from src.utils.languageFilter import LanguageFilter
from src.utils.configProvider import ConfigProvider


class ElPaisParser(GenericParser):

    def __init__(self):
        super(ElPaisParser, self).__init__()
        self.language_filter = LanguageFilter()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    source = u'El País'

    def parse(self, url):
        soup = BeautifulSoup(urlopen(url).read())
        paragraphs = ''
        tags = []
        new_entries = []
        title = ''
        if soup is not None:
            news_body = soup.find('div', {'id': 'cuerpo_noticia'})
            if news_body is not None:
                paragraphs = [p.text + '\n' for p in news_body.find_all(
                    'p')]
                container = soup.find('div',
                                      {'class': 'contenedor'})
                if container is not None:
                    list_tag = container.find(
                        'ul').find_all('li')
                    tags = [li.find('a').text for li in list_tag]
  
        title_obj = soup.find('h1', {'id': 'titulo_noticia'})
        if title_obj is not None:
            title = title_obj.text
              
        content = ' '.join(paragraphs)
        content = self.sanitize(content)

        news_parsed = None

        if len(content) > 1 and len(tags) > 0 and len(title) > 0:
            news_parsed = NewsEntry(title, content, tags, self.source, url=url)

        return news_parsed
