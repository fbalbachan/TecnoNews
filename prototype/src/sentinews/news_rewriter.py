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
import re

import wikipedia as wk
logger = get_logger('tecnonews')

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
                                         original_entry.source,
                                         related=original_entry.related,
                                         versions=original_entry.versions)

    def _get_alt_text(self, im, h):
        im2 = [(x.split('/')[-1].split('.')[0], x) for x in im]

        res = {}
        for img,url in im2:
            try:
                x = re.search("\<img.*%s.*/>" % img, h).group(0)
                s = re.search("alt=\".*\" src=", x).group(0)
                s = s[s.find('"')+1:]
                s = s[:s.find('"')]
                res[url] = s
            except:
                res[url] = url
        return res

    def insert_main_image(self, wikipage):
        ## TODO CAMBIAR

        img_alts = self._get_alt_text(wikipage.images, wikipage.html())
        images = img_alts.keys()

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
        if not images:
            return self.rewritten_entry.content
        if res:
            image = res[0]
        else:
            image = images[0]
        
        logger.info("IMAGE URL: %s %s", image, img_alts[image])

        return '<p><img title="%s" src=%s></img></p> <p><small>%s</small></p> %s' %(img_alts[image], image,img_alts[image], self.rewritten_entry.content)

    def rewrite_title(self):
        analysis = self._analyze(self.original_entry.title)
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.title = rewriter.rewrite()
        self.rewritten_entry.title = self.original_entry.title

    def rewrite_content(self):
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
            logger.info("WIKIINFO: %s", str(wikiinfo))
            self.rewritten_entry.content  = self.insert_main_image(wikiinfo[0][2])
        else:
            logger.info("NO REFERENT SCORE > 1")

    def publish(self):
        publisher = BlogPublisher()
        publisher.publish(self.rewritten_entry)

    def _analyze(self, text):
        return Sentilecto().analyze(text)

