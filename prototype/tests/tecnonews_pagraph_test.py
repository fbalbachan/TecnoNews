# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_rewriter import NewsRewriter
from src.utils.logger_utils import *
from src.utils.relatedNewsEntries import RelatedNewsEntries
import traceback

class TecnonewsTest(unittest.TestCase):
    ''' Clase para testear una sola noticia end to end '''
    service = NewsEntriesService()
    news_entry = None
    object_id = None

    def test_end_2_end(self):
        logger = get_logger('tecnonews')
        other_versions = []
        nes = NewsEntriesService()
        # entry = nes.get_list({'title': 'Fiscalía pide el internamiento de cuatro menores detenidos en Lleida'})[0]
        entry = nes.get_list({'title': 'Unión Europea estudia nuevas sanciones contra Rusia'})[0]
        entry.set_analisys_info()

        try:
            tsr = RelatedNewsEntries(entry)
            other_versions = tsr.get_other_versions_top_ten()
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
        c.rewritten_entry.other_versions = other_versions

        logger.info('<Tecnonews> <_process> publishing note: ' + entry.source)
        try:

            # c.rewrite_title()
            c.rewrite_content()
            c.publish()
            # entry.published_date = datetime.utcnow()
            # entry.wp_id = c.rewritten_entry.wp_id
            # pass
        except Exception, e:
            logger.error("<Tecnonews> <_process> rewriting fail: %s " % (entry.title))
            logger.info(traceback.format_exc())



if __name__ == '__main__':
    unittest.main()