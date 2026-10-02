#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from urllib.parse import urlparse


class ElMundoParser(GenericParser):
    def __init__(self):
        super(ElMundoParser, self).__init__()

    source = "El Mundo"

    def parse(self, url):
        if '/opinion/' in url:
            return None
        #url  = "http://www.elmundo.es/espana/2016/06/01/574f24bf22601df96e8b4612.html"
        #url  = "http://www.elmundo.es/economia/2016/01/26/56a61a39ca474156648b466c.html"
        soup = BeautifulSoup(self.opener.read(url))
        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "redes-sociales"}):
            social.extract()

        # Remove trash
        for atext in soup.findAll(True,{"class": ["image", "aside-tools", "summary-lead"]}):
            atext.extract()

        #Canta: noticias relacionadas.
        for aside in soup(["aside", {"class":"related-links"}]):
            aside.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        new_entry = None
        title = soup.find('h1', {"class": "js-headline"}).text
        categories = [urlparse(url).path.split("/")[1]]

        des = soup.find('article', {"class": "desarrollo"})

        #image_search_string = des.find('header').find('h2').text + u' '
        image_search_string = title.split('.')[0]

        tags = set()

        tag_links = soup.findAll('section', {"class": "tags"})
        for tag in tag_links:
            links = tag.findAll('a')
            for l in links:
                if l.text.lower() != 'tags':
                    tags.add(l.text)

        tag_links = soup.findAll('ul', {"class": "item-tags"})
        for tag in tag_links:
            links = tag.findAll('a')
            for l in links:
                if l.text.lower() != 'tags':
                    tags.add(l.text)


        content = ""
        for a_paragraph in soup.find('div', {"data-section": 'articleBody'}).findAll('p'):
            content += "\n" + a_paragraph.text.strip()

        content = content.strip()
        #return {"content" : content, "title":title, "tags": tags, "image_search_string":image_search_string}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

if __name__ == "__main__":
    ElMundoParser().parse("https://www.elmundo.es/espana/2019/04/26/5cc36c9cfc6c830d038b4615.html")
