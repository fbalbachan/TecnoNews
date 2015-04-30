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


class EuroNewsParser(GenericParser):
    def __init__(self):
        super(EuroNewsParser, self).__init__()
        self.language_filter = LanguageFilter()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    base_path = 'http://es.euronews.com'
    source = u'Euronews'

    def parse(self, url):
        soup = BeautifulSoup(urlopen(url).read())
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


        news_parsed = None
        if len(content) > 1 and len(tags) > 0 and len(title) > 0:
            news_parsed = NewsEntry(title, content, tags, self.source, url=url)

        return news_parsed
