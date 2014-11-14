# -*- coding: utf-8 -*-
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
import datetime

logger = get_logger('tecnonews')

class TecnoNews(object):
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
          c = NewsRewriter(entry)
          logger.info("publishing note: " + entry.source)
          #c.rewrite()
          #c.publish()
        except Exception, e:
            logger.info(traceback.format_exc())

if __name__ == '__main__':
    TecnoNews().run()
