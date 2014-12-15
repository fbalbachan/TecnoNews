#!/usr/bin/python
# -*- coding: utf-8 -*-
from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *
from src.utils.languageFilter import LanguageFilter
from ConfigParser import ConfigParser

class ElPaisParser(object):

    def __init__(self):
        self.language_filter = LanguageFilter()
        config = ConfigParser()
        config.read('config')
        self.language_filter_status = config.get('language_filter', 'status')

    source = u'El País'

    def parse(self, url, limit=1):
        soup = BeautifulSoup(urlopen(url).read())
        articles = soup.find_all('div', {'class': 'article estirar'}, limit=limit)
        new_entries = []
        if articles is not None:
            for article in articles:
                title = article.find('h2').find('a').text
                article_url = article.find('h2').find('a')['href']
                content, tags = self.__extract_content(article_url)

                if self.language_filter_status == 'ON':
                    content = self.language_filter.only_spanish_paragraph(content.encode("utf-8"))

                if len(content) > 1 and len(tags) > 0:
                    new_entries.append(NewsEntry(title, content, tags, self.source, article_url))
        return new_entries


    def __extract_content(self, article_url):
        soup = BeautifulSoup(urlopen(article_url).read())
        content = ''
        tags = []
        if soup is not None:
            news_body = soup.find('div', {'id': 'cuerpo_noticia'})
            if news_body is not None:
                content = [p.text + '\n' for p in news_body.find_all(
                    'p')]
                container = soup.find('div',
                                      {'class': 'contenedor'})
                if container is not None:
                    list_tag = container.find(
                        'ul').find_all('li')
                    tags = [li.find('a').text for li in list_tag]

        return " ".join(content), tags