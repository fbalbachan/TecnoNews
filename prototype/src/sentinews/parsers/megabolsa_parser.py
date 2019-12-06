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


class MegaBolsaParser(GenericParser):
    source = u"MegaBolsa"
    dolog = False

    def __init__(self):
        super(MegaBolsaParser, self).__init__()

    def log(self, *args):
        if self.dolog:
            print((" ".join(unicode(x) for x in args)))

    def parse(self, url):
        return self.parse_soup(BeautifulSoup(self.opener.read(url)), url)

    def parse_soup(self, soup, url):
        title = soup.find('h1', {"class": "entry-title"})
        title = title.text.strip()
        self.log("title:", title)

        content = ""
        article_content = soup.find('div', {"class": "entry-content"}).findAll('p')
        for paragraph in article_content:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        self.log("content:", content)
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=["economia"],
                                           source=self.source,
                                           url=url,
                                           original_categories=["economia"],
                                           image_search_string=None,
                                           keywords=None)
        return new_entry


if __name__=="__main__":
    import requests
    url = sys.argv[1]
    p = MegaBolsaParser()
    p.dolog = True
    p.parse(url)

