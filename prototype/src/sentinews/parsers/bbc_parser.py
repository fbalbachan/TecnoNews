#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class BBCParser(GenericParser):
    def __init__(self):
        super(BBCParser, self).__init__()

    source = 'BBC'

    def parse(self, url, tags=None):
        if u'/video_fotos/' in url:
            return None

        content = None
        title = None
        soup = BeautifulSoup(self.opener.read(url), "html.parser")
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        for link in soup.findAll('a', {'class': 'story-body__link'}):
            link.extract()

        for link in soup.findAll('a', {'class': 'story-body__link-external'}):
            link.extract()

        if soup:
            article = soup.find('div', {'class': 'story-body'})
            if article is not None:
                title = article.find('h1', {'class': 'story-body__h1'}).text
                paragraphs = article.find('div', {'class': 'story-body__inner'}).find_all('p')
                content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])
                # content = self.sanitize(content)

        categories = None
        image_search_string = None

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)
        return new_entry
