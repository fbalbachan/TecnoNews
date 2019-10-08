#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re
from src.utils.unicodeTools import safe_unicode


class LaNacionPropiedadesParser(GenericParser):
    def __init__(self):
        super(LaNacionPropiedadesParser, self).__init__()

    source = u"la_nacion_propiedades"
    
    def parse(self, url):
        # url = "http://www.lanacion.com.ar/1882840-nave-industrial-para-el-desarrollo-logistico"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        for image in soup.findAll('img'):
            image.extract()

        for aside in soup.findAll('aside',{'class':'mas-sobre-tema'}):
            aside.extract()

        title = soup.find('', {'class':'titulo'})
        title = title.text.strip()

        content = "" 
        
        intro = soup.find('p',{'class':'bajada'})
        if intro:
            content += intro.text.strip() + "."

        paragraphs = soup.find('section',{'id':'cuerpo'}).findAll(['p','h2'])

        for paragraph in paragraphs:
            clean_text = re.sub(u'[ ]{2,}', ' ', paragraph.text.strip())
            content += "\n" + clean_text

        content = content.strip()

        title = safe_unicode(title)
        content = safe_unicode(content)
        
        tags = [u"propiedades"]
        categories = [u"propiedades"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
