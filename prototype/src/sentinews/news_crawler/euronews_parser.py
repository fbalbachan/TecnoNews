#!/usr/bin/python
# -*- coding: utf-8 -*-
from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *


class EuroNewsParser(object):
    base_path = 'http://es.euronews.com'
    source = u'Euronews'

    def parse(self, url, limit=1):
        soup = BeautifulSoup(urlopen(url).read())
        articles = soup.find(
            'ul', {'id': 'bulletin-list'}).find_all('li', limit=limit)

        new_entries = []
        for article in articles:
            title = title = article.find(
                'span', {'class': 'bulletin-title'}).text[12:]
            content, tags = self.___extract_content(article)
            if len(content) > 1:
                new_entries.append(NewsEntry(title, content, tags, self.source))

        return new_entries


    def ___extract_content(self, article):
        article_url = article.find('a', {'class': 'read-more-button'})['href']
        soup = BeautifulSoup(urlopen(self.base_path + article_url).read())
        if soup is not None:
            paragraphs =  None
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
                li_tags = soup.find('ul', {'class': 'kwl'}).find_all('li')
                tags = [tag.find('a').text for tag in li_tags]
            return " ".join(content_str), tags
        else:
            return ''
