#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
try:
    from src.sentinews.parsers.generic_parser import GenericParser
except:
    import requests
    class GenericParser(object):
        class _opener:
            def read(self, url):
                r = requests.get(url)
                return r.text

        @property
        def opener(self):
            return self._opener()

        def create_news_entry(self, **kw):
            return kw


class BloombergParser(GenericParser):
    """this isn't actually working: server seems to reject our user agent!"""
    source = "Bloomberg"
    dolog = False

    def __init__(self):
        super(BloombergParser, self).__init__()

    def log(self, *args):
        if self.dolog:
            print((" ".join(str(x) for x in args)))

    def parse(self, url):
        page = self.opener.read(url)
        # print("page:", page)
        return self.parse_soup(BeautifulSoup(page), url)

    def parse_soup(self, soup, url):
        title = soup.find('div', {'class': 'headline-section'}). find('h1', {"class": 'h1-regular-7'}).text.strip()
        #pretags = soup.find('span', {"class": 'tags'}).findAll("a")
        tags = set() #set(x.text.strip() for x in pretags)
        self.log("title:", title)

        content = ""
        paragraphs1 = soup.findAll('div', {"class": 'wpb_wrapper'})
        for paragraph in paragraphs1:
            for para in paragraph.find('div', {"class": 'wpb_wrapper'}).findAll('p'):
                clean_text = para.text.strip()
                content += "\n" + clean_text
        content = content.strip()
        self.log("content:", content)
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=["economia"],
                                           source=self.source,
                                           url=url,
                                           original_categories=["economia"],
                                           image_search_string="",
                                           keywords=None)
        return new_entry


if __name__=="__main__":
    import requests
    url = sys.argv[1]
    p = BloombergParser()
    p.dolog = True
    p.parse(url)

