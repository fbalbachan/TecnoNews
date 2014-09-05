# -*- coding: utf-8 -*-

from src.model.sentilecto import Sentilecto
from src.sentinews.hyperlink_processor import HyperlinkProcessor
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry

class NewsRewriter(object):
    ''' Main class that contains all information 
        about the original news article and
        the rewritten result. 
        Ties the crawler, the rewrite strategies and
        the publisher. '''
    
    def __init__(self, original_entry):
        self.original_entry = original_entry
        self.rewritten_entry = NewsEntry(original_entry.title,
                                         "",
                                         original_entry.tags,
                                         self.original_entry.source)
    
    def rewrite(self):
        analysis = self._analyze(self.original_entry.content)

        hyperlink_processor = HyperlinkProcessor(analysis)
        self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()

    def publish(self):
        publisher = BlogPublisher()
        publisher.publish(self.rewritten_entry)

    def _analyze(self, text):
        return Sentilecto().analyze(text)

