#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser


class ABCParser(GenericParser):
    def __init__(self):
        super(ABCParser, self).__init__()

    source = "ABC"

    def parse(self, url):
        if '/silencio-por-favor/' in url:
            return None

        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')
                             #from_encoding='iso-8859-15')

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "redes-sociales"}):
            social.extract()

        for ante in soup.findAll('span', {"class": "antetitulo-noticia"}):
            ante.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        title = soup.find('h1', {"itemprop": "name headline"})

        if not title:
            #title = soup.find('span', {"itemprop": "headline"})
            title = soup.find('span', {"class": "titulo-noticia"})

        title = title.text.strip()
        #title = title.decode("iso-8859-15")
        categories = [urlparse(url).path.split("/")[1]]

        # des = soup.find('article', {"class": "desarrollo"})
        # image_search_string = des.find('header').find('h2').text + u' '
        # image_search_string += title.split('.')[0]

        # No tags
        tags = set()

        #content = soup.find('div', {"itemprop": 'articleBody'}).text

        content = ""
        paragraphs = soup.find('div', {"itemprop": 'articleBody'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text

        content = content.strip()

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
