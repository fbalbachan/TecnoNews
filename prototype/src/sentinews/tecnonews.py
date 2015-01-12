# -*- coding: utf-8 -*-
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.relatedNewsEntries import RelatedNewsEntries
from src.utils.logger_utils import *
import traceback
from datetime import datetime

logger = get_logger('tecnonews')

class TecnoNews(object):

    def __init__(self):
      self.service = NewsEntriesService()

    def test(self):
      logger.info("OKOK")

    def run(self):
        logger = get_logger('tecnonews')
        logger.info("<Tecnonews> <run> Running start")
        entries =  NewsCrawler().crawl_all()
        logger.info("Entries to publish: %s" % len(entries))

        for entry in entries:
            self._process(entry)
        logger.info("Done.")

    def _process(self, entry):
        try:
            entry.set_analisys_info()
            try:
                tsr = RelatedNewsEntries(entry)
                related_news = tsr.get_related()
                entry.set_related_news(related_news)
                logger.info("<Tecnonews> <_process> related_news number %s" % len(related_news))
            except Exception, e:
                logger.error("<Tecnonews> <_process> related_news %s" % entry.title)
                logger.error("<Tecnonews> <_process> related_news %s" % traceback.format_exc())

            c = NewsRewriter(entry)

            logger.info('<Tecnonews> <_process> publishing note: ' + entry.source)
            try:
                # c.rewrite_title()
                c.rewrite_content()
                c.publish()
                entry.publish_date = datetime.utcnow()
                entry.wp_id = c.rewritten_entry.wp_id
            except Exception, e:
                logger.error("<Tecnonews> <_process> rewriting fail: %s " % (entry.title))

        except Exception, e:
            logger.info(traceback.format_exc())

        # Always save
        self.service.save(entry)



if __name__ == '__main__':
    TecnoNews().run()
