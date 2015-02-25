# -*- coding: utf-8 -*-
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler import NewsCrawler
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.relatedNewsEntries import RelatedNewsEntries
from src.utils.logger_utils import *
import traceback
from datetime import datetime

logger = get_logger('tecnonews')


class TecnoNews(object):
    def __init__(self):
        self.service = NewsEntriesService()

    def run(self):
        logger = get_logger('tecnonews')
        logger.info("<Tecnonews> <run> Running start")
        entries = NewsCrawler().crawl_all()

        logger.info("<Tecnonews> <run> Entries to publish: %s" % len(entries))

        for idx, entry in enumerate(entries):
            logger.info("<Tecnonews> <run> processing entry %s of %s" % (idx, len(entries)))
            self._process(entry)
        logger.info("<Tecnonews> <run> Done.")

    def _process(self, entry):
        logger.info("<Tecnonews> <_process> START processing %s" % entry.title)
        other_versions = []
        try:
            entry.set_analisys_info()
            try:
                tsr = RelatedNewsEntries(entry)
                other_versions = tsr.get_other_versions_top_ten()
                entry.set_news_versions(other_versions)
                related = tsr.get_related_entities_top_5_not_in_list(other_versions)
                entry.set_related_news(related)
                logger.info("<Tecnonews> <_process> same news different coverage number %s" % len(other_versions))
                logger.info("<Tecnonews> <_process> related_news number %s" % len(related))
            except Exception as e:
                logger.error("<Tecnonews> <_process> related_news %s" % entry.title)
                logger.error("<Tecnonews> <_process> related_news %s" % e.message)
                logger.error("<Tecnonews> <_process> related_news %s" % traceback.format_exc())
                logger.info(traceback.format_exc())

            rewriter = NewsRewriter(entry)
            # Add the other_version entries (only ids) to be used in paragraph insertion
            rewriter.rewritten_entry.other_versions = other_versions

            logger.info('<Tecnonews> <_process> rewriting note: ' + entry.title)
            try:
                # rewriter.rewrite_title()
                rewriter.rewrite_content()
                logger.info('<Tecnonews> <_process> publishing: ' + entry.title)
                wp_id, wp_url = rewriter.publish()
                entry.wp_id = wp_id
                entry.wp_url = wp_url

                # TODO: check if we must use datetime from wp
                entry.published_date = datetime.utcnow()

            except Exception as e:
                logger.error("<Tecnonews> <_process> rewriting fail: %s " % entry.title)
                logger.error("%s" % e.message)
                logger.info(traceback.format_exc())

        except Exception as e:
            logger.info(traceback.format_exc())
            logger.error("%s" % e.message)

        self.service.save(entry)

        logger.info("<Tecnonews> <_process> END processing %s" % entry.title)


if __name__ == '__main__':
    TecnoNews().run()
