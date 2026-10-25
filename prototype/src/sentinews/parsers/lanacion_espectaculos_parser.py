#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class LaNacionEspectaculosParser(GenericParser):
    def __init__(self):
        super(LaNacionEspectaculosParser, self).__init__()

    source = "La Nacion espectaculos"

    def is_parseable_case(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))


        tema_nota = soup.find('span', {"class": "tema-nota"})
        print("tema_nota %s" % tema_nota)

        dislowed_keywords = ['Bailando por un sueño',
                             'Conversaciones',
                             'LA NACION',
                             'look']

        if tema_nota and any(k for k in dislowed_keywords if k in tema_nota):
            allowed = False

        return allowed

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable_case(url=url, soup=soup):
            return None

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "herramientas"}):
            social.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        title = soup.find('h1', {"class": "titulo"})

        title = title.text.strip()

        #categories = None
        #category = soup.find('span', {"itemprop": "title"}).text

        #tags = [category]

        #content = soup.find('section', {"itemprop": 'articleBody'}).text

        content = ""
        paragraphs = soup.find('section', {"id": 'cuerpo'}).findAll('p')
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        tags=['entretenimiento']
        categories=['entretenimiento']
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

if __name__ == "__main__":
    LaNacionEspectaculosParser().parse("https://www.lanacion.com.ar/espectaculos/television/showmatch-quien-es-figura-mas-cara-pista-nid2241559")
