#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from urlparse import urlparse
from src.utils.unicodeTools import safe_unicode

class ArqaParser(GenericParser):
    def __init__(self):
        super(ArqaParser, self).__init__()

    source = 'arqa'

    def parse(self, url, tags=None):

        #url = "http://arqa.com/agenda/lanzamiento-convocatoria-bia-ar-2016.html"

        content = None
        title   = u""
        soup    = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        if soup:
            article = soup.find("section", { "id" : "content"})
            if article is not None:
                title      = article.find("h1", class_ = "title").text.strip()
                
                paragraphs = article.find_all('p')[2:] # los primeros dos son otra cosa.
                if paragraphs is not None and len(paragraphs) > 0 :
                    content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])
        
        categories  = [u"propiedades"]
        tags        = [u"propiedades"]
        
        title   = safe_unicode(title)
        content = safe_unicode(content)
        
        image_search_string = None
        
        #return {"title" : title, "content" : content}

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)
        return new_entry
