#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from urllib.parse import urlparse


class EuropaPressParser(GenericParser):
    def __init__(self):
        super(EuropaPressParser, self).__init__()

    source = "EuropaPress"

    def parse(self, url):
        # if u'/silencio-por-favor/' in url:
        #     return None

        soup = BeautifulSoup(self.opener.read(url))

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "at-floatingbar-share"}):
            social.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        new_entry = None
        title = soup.find('h1', {"itemprop": "headline"})

        if not title:
            title = soup.find('span', {"itemprop": "headline"})

        title = title.text.strip()

        categories = [urlparse(url).path.split("/")[1]]

        # des = soup.find('article', {"class": "desarrollo"})
        # image_search_string = des.find('header').find('h2').text + u' '
        # image_search_string += title.split('.')[0]

        # No tags
        tags = set()

        tags_ul = soup.find('ul', {"class": "entidadesNoticiav2"})

        links = tags_ul.findAll('a')
        for l in links:
            tags.add(l.text)

        content = soup.find('div', {"itemprop": 'articleBody'})
        date_div = content.findAll('div', {'class': 'FechaPublicacionNoticia'})
        for dd in date_div:
            dd.extract()

        p_content = ''
        all_p_in_content = content.findAll('p')
        if 'EUROPA PRESS' in all_p_in_content[0].text:
            all_p_in_content.pop(0)

        for p in all_p_in_content:
            p_content += p.text + '\n'

        content = p_content

        # TODO make a cleanning method in each parser and leave only common in
        # the sanitize process
        import re
        content = re.sub('\(EUROPA PRESS\) ?(-|–)?', '', content)
        content = re.sub('\(EDIZIONES\) ?(-|–)?', '', content)

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

