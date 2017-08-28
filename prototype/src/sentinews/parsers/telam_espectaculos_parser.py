#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class TelamEspectaculosParser(GenericParser):
    def __init__(self):
        super(TelamEspectaculosParser, self).__init__()
        # config = ConfigProvider()
        # self.language_filter_status = config.get('language_filter', 'status')

    source = u"Telam Espectaculos"

    def get_categories(self, soup):
        categories = None
        section = soup.find('div', {"class": 'secs clearfix'})
        active = section.find('a', {"class": 'active'})

        if active:
            section_text = active.text
            categories = list(section_text)

        if not categories:
            categories = [u'espect\xe1culos']

        return categories

    def is_parseable_case(self, url):

        soup = BeautifulSoup(self.opener.read(url))
        categories = self.get_categories(soup)
        fobiden_sections = [u'televisi\xf3n']
        if any(k for k in fobiden_sections if k in categories):
            return False
        else:
            return True

    def parse(self, url):
        # if not self.is_parseable_case(url):
        #    return None
        # url = "http://www.telam.com.ar/notas/201606/150421-robert-plant-y-jimmy-page-estaran-presentes-en-el-juicio-por-supuesto-plagio.html"
        soup = BeautifulSoup(self.opener.read(url), "html.parser", from_encoding='windows-1252')
        # categories = self.get_categories(soup)

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('div', {"class": "head-media"}):
            social.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        title = soup.find('div', {"class": ["title", "head-content"]}).find('h2').text.strip()
        content = soup.find('div', {"class": 'editable-content'}).text

        tags = [u'entretenimiento']
        categories = [u'entretenimiento']

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
