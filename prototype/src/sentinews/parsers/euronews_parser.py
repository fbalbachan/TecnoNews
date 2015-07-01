#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class EuroNewsParser(GenericParser):
    def __init__(self):
        super(EuroNewsParser, self).__init__()

    base_path = 'http://es.euronews.com'
    source = u'Euronews'

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        paragraphs = None
        tags = []
        title = ''
        if soup is not None:
            try:
                paragraphs = soup.find('div', {'id': 'articleTranscript'}).find_all('p')
            except Exception as e:
                logger = get_logger('tecnonews')
                logger.error("Problem Parsing euronews new..")
                logger.error(e.message)

            if paragraphs is not None:
                content_paragraphs_list = [paragraph.text for paragraph in paragraphs]
            else:
                content_paragraphs_list = []

            content_str = [text + '\n' for text in content_paragraphs_list]
            tags = []
            if paragraphs is not None:
                ul_tags = soup.find('ul', {'class': 'kwl'})
                if not ul_tags is None:
                    li_tags = soup.find('ul', {'class': 'kwl'}).find_all('li')
                    tags = [tag.find('a').text for tag in li_tags]
            content = " ".join(content_str)
        else:
            content = ''

        content = self.sanitize(content)

        title_obj = soup.find(
            'div', {'id': 'title-wrap-new'}).find('h1').find('a')

        if title_obj is not None:
            title = title_obj.text

        import re
        title = re.sub(u'Fotos:( )*', u'', title)
        title = title[0].upper() + title[1:]

        new_entry = self.create_news_entry(title, content, tags, self.source, url, categories,
                                           image_search_string)

        return new_entry
