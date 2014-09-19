# -*- coding: utf-8 -*-

from src.model.sentilecto import Sentilecto
from src.sentinews.hyperlink_processor import HyperlinkProcessor
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.extension.textInserter import TextInserter
from src.rewrite.rewriter import Rewriter
from src.model.referent.referentRanker import ReferentRanker
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.utils.logger_utils import *


import wikipedia as wk

class NewsRewriter(object):
    ''' Main class that contains all information 
        about the original news article and
        the rewritten result. 
        Ties the crawler, the rewrite strategies and
        the publisher. '''
    
    def __init__(self, original_entry):
        self.original_entry = original_entry
        self.rewritten_entry = NewsEntry(original_entry.title,
                                         original_entry.content,
                                         original_entry.tags,
                                         original_entry.source)
    
    def inject_additional_info(self, wikipage):
        self.insert_main_image(wikipage)

    def insert_main_image(self, wikipage):
        ## TODO CAMBIAR

        images = wikipage.images
        search_string = wikipage.original_title.lower().split()

        res = []
        for x in search_string:
            if len(x) < 4:
                continue

            for y in images:
                if x in y.lower():
                    if 'logo' in y:
                        res = [y]
                    else:
                        if y not in res:
                            res.append(y)

        for x in res:
            if "Flag" in x:
                res = [x]
                break
        if res:
            image = res[0]
        else:
            image = images[0]

        return "<img src=%s></img> %s" %(image, self.rewritten_entry.content)



    def rewrite(self):
        analysis = self._analyze(self.original_entry.content)
        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()
        analysis["generated_content"] = WikipediaContentGenerator(analysis).generate()
        text_inserter = TextInserter(analysis)
        self.rewritten_entry.content = text_inserter.get()

        wikiinfo =  analysis["generated_content"]
        ranking =  analysis["referent_ranking"]

        analysis = self._analyze(self.rewritten_entry.content)
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.content = rewriter.rewrite()

        analysis = self._analyze(self.rewritten_entry.content)
        hyperlink_processor = HyperlinkProcessor(analysis)
        self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()

        if wikiinfo and filter(lambda (referent, score): referent == wikiinfo[0][0] and score > 1., ranking): 
            self.rewritten_entry.content  = self.insert_main_image(wikiinfo[0][2])

    def publish(self):
        publisher = BlogPublisher()
        publisher.publish(self.rewritten_entry)

    def _analyze(self, text):
        return Sentilecto().analyze(text)

