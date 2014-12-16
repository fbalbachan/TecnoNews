# -*- coding: utf-8 -*-
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *
import traceback
import datetime

logger = get_logger('tecnonews')

class TecnoNews(object):

    def __init__(self):
      self.service = NewsEntriesService()


    def test(self):
      logger.info("OKOK")


    def run(self):
      logger = get_logger('tecnonews')
      entries =  NewsCrawler().crawl_all()
      logger.info("Entries to publish: %s" % len(entries))
      for entry in entries:
        self._process(entry)
      logger.info("Done.")


    def _process(self, entry):
        try:
          # logger.info("original")
          # logger.info(entry.content)
          c = NewsRewriter(entry)
          logger.info("publishing note: " + entry.source)
          try:   
            c.rewrite()
          except Exception, e:
            logger.error("rewrite for new(%s) fails. " % (entry.title))
          
          # logger.info("rewrited")
          # logger.info(c.rewritten_entry.content)
          
          self.service.save(entry)

          c.publish()
        except Exception, e:
            logger.info(traceback.format_exc())


if __name__ == '__main__':
    TecnoNews().run()
