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
                other_versions = tsr.get_other_versions()
                entry.set_news_versions(other_versions)
                related = tsr.get_related_entities_top_5_not_in_list(other_versions)
                entry.set_related_news(related)
                logger.info("<Tecnonews> <_process> samenews diferente coverage number %s" % len(other_versions))
                logger.info("<Tecnonews> <_process> related_news number %s" % len(related))
            except Exception, e:
                logger.error("<Tecnonews> <_process> related_news %s" % entry.title)
                logger.error("<Tecnonews> <_process> related_news %s" % traceback.format_exc())
                logger.info(traceback.format_exc())

            c = NewsRewriter(entry)

            logger.info('<Tecnonews> <_process> publishing note: ' + entry.source)
            try:
                # c.rewrite_title()
                c.rewrite_content()
                c.publish()
                entry.published_date = datetime.utcnow()
                entry.wp_id = c.rewritten_entry.wp_id
            except Exception, e:
                logger.error("<Tecnonews> <_process> rewriting fail: %s " % (entry.title))
                logger.info(traceback.format_exc())
        except Exception, e:
            logger.info(traceback.format_exc())

        # Always save
        logger.info("<<<")
        logger.info("entry : %s" % entry.title)
        logger.info("relateds: %s" % entry.related)
        self.service.save(entry)



if __name__ == '__main__':
    TecnoNews().run()
