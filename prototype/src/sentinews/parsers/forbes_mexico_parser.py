#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class ForbesMexicoParser(GenericParser):
    def __init__(self):
        super(ForbesMexicoParser, self).__init__()

    source = u"Forbes Mexico"

    def parse(self, url):

        # url = "http://www.forbes.com.mx/remesas-mexico-suben-8-3-abril/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+ForbesMexico+%28Forbes+M%C3%A9xico%29"
        # url = "http://feedproxy.google.com/~r/ForbesMexico/~3/PoUldQ3tza8/"
        soup = BeautifulSoup(self.opener.read(url))
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        # title = soup.find('h1', {"itemprop": "headline"})
        title = soup.find('h1', {"class": "entry-title"})
        title = title.text.strip()

        metadata = soup.find('meta', {'property': 'article:section'})

        # metadata = soup.find('ul', {"class": "meta"})
        # OLD METHOD WORKING?
        # category = metadata.find(href=re.compile('/category/'))

        categories = [metadata['content'], "economia"]

        # NEW METHOD:
        '''
        if category is None:
            category = metadata.findAll("li")
            category = category[1:]
            category = category[:-1]
            for a_category in category:
                categories.append(a_category.text.strip())
        else:
            categories = [category.text.strip()]
        '''

        tags = set()
        for tag in soup.findAll('meta', {'property': 'article:tag'}):
            tags.add(tag['content'].strip())

        # content = soup.find('section', {"itemprop": 'articleBody'}).text
        content = soup.find(True, {"class": 'entry-content'}).text

        tags = list(tags)
        # return {"content":content, "tags":tags, "categories": categories, "title":title }
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
