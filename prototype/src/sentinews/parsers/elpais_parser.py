#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class ElPaisParser(GenericParser):

    def __init__(self):
        super(ElPaisParser, self).__init__()

    source = u'El País'

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        paragraphs = ''
        tags = []
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
        if u'El resumen del d\xeda de El Pa\xeds' in title:
            title = None

        content = ' '.join(paragraphs)

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=None,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
