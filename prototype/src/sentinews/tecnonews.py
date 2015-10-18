# -*- coding: utf-8 -*-
import traceback

from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler import NewsCrawler
from src.utils.freelingLanguageDetectorClient import FreelingLanguageDetectorClient
from src.utils.freelingClientParser import FreelingClientParser
from src.utils.textDistance import TextDistance
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.relatedNewsEntries import RelatedNewsEntries
from src.utils.logger_utils import *
from src.utils.configProvider import ConfigProvider
from bs4 import BeautifulSoup
from datetime import datetime

logger = get_logger('tecnonews')
logger_similarity = get_logger_similarity()


class TecnoNews(object):
    def __init__(self, config_provider=None):

        if not config_provider:
            self.config = ConfigProvider()
        else:
            self.config = config_provider

        self.instance = get_instance_info()
        self.freeling_lang_ident = FreelingLanguageDetectorClient()
        self.freeling_parse = FreelingClientParser()
        self.service = NewsEntriesService()
        self.published_in_this_run = 0
        self.not_published_in_this_run = 0

    def environment_health(self):
        li_health = self.freeling_lang_ident.health_check()
        parse_health = self.freeling_parse.health_check()
        return li_health and parse_health

    def run(self):
        logger = get_logger('tecnonews')
        logger.info("<Tecnonews> <run> --> STARTED -------------------------------------------------------------------")

        self.published_in_this_run = 0
        self.not_published_in_this_run = 0

        logger.info("<Tecnonews> <run> --> STARTING TO CRAWL FEEDS")
        entries = NewsCrawler().crawl_all()

        logger.info("<Tecnonews> <run> <-- FINISHED CRAWLING - Entries fetched: %s" % len(entries))
        for idx, entry in enumerate(entries):
            logger.info("<Tecnonews> <run> Processing entry %s of %s" % (idx, len(entries)))
            self._process(entry)

        logger.info("<Tecnonews> <run> ----- BRIEFING ----------------------------------------------------------------")
        logger.info("<Tecnonews> <run> Number of Freeling_Lang_Identification calls: %s" % self.freeling_lang_ident.calls_count)
        logger.info("<Tecnonews> <run> Published entries: %s" % self.published_in_this_run)
        logger.info("<Tecnonews> <run> NOT published entries: %s" % self.not_published_in_this_run)
        logger.info("<Tecnonews> <run> -------------------------------------------------------------------------------")

        logger.info("<Tecnonews> <run> <-- FINISHED ------------------------------------------------------------------")

    def log_similarity_info(self, rewriter, valid_to_publish):
        logger_similarity.info("\n\n----- --> SIMILARITY INFO ----------------------------------------------------\n\n")
        logger_similarity.info("<similarity> url: %s\n" % rewriter.original_entry.url)

        logger_similarity.info("<similarity> Original content: ")
        logger_similarity.info("--> [%s]" % rewriter.original_entry.content)

        logger_similarity.info("<similarity> Rewritten content: ")
        clean_rewritten = BeautifulSoup(rewriter.rewritten_entry.content).getText()
        logger_similarity.info("--> [%s]" % clean_rewritten)

        logger_similarity.info("\n\n<similarity> Valid to publish: %s " % valid_to_publish)
        logger_similarity.info("\n\n----- <-- SIMILARITY INFO ----------------------------------------------------\n\n")

    def _process(self, entry):
        logger.info("<Tecnonews> <_process> --> STARTED _process([%s])" % entry.title)
        other_versions = []
        try:
            entry.set_analysis_info()
            try:
                tsr = RelatedNewsEntries(entry)
                other_versions = tsr.get_other_versions_top_ten()
                entry.set_news_versions(other_versions)
                logger.info("<Tecnonews> <_process> Number of Same_News_Coverages: %s" % len(other_versions))

                related = tsr.get_related_entities_top_5_not_in_list(other_versions)
                entry.set_related_news(related)
                logger.info("<Tecnonews> <_process> Number of Related_news: %s" % len(related))

            except Exception as e:
                logger.error("<Tecnonews> <_process> <-- FAILED relating news (Title: %s)" % entry.title)
                logger.error("<Tecnonews> <_process> Exception: %s" % e.message)
                logger.error("<Tecnonews> <_process> Traceback: \n%s" % traceback.format_exc())

            try:
                logger.info('<Tecnonews> <_process> --> STARTED Rewriting: ' + entry.title)

                rewriter = NewsRewriter(entry)
                # Add the other_version entries (only ids) to be used in paragraph insertion
                rewriter.rewritten_entry.other_versions = other_versions
                rewriter.rewrite_title()
                rewriter.rewrite_content()

                logger.info('<Tecnonews> <_process> <-- FINISHED Rewriting: ' + entry.title)

                logger.info('<Tecnonews> <_process> --> STARTED Publishing logic')

                valid_to_publish = self.valid_to_publish(rewriter)
                self.log_similarity_info(rewriter, valid_to_publish)
                if valid_to_publish:
                    logger.info('<Tecnonews> <_process> Publishing... (Title: %s)' % entry.title)
                    wp_id, wp_url = rewriter.publish()
                    entry.wp_id = wp_id
                    entry.wp_url = wp_url
                    entry.published_date = datetime.utcnow()    # TODO: check if we must use datetime from wp
                    self.published_in_this_run += 1
                    if wp_id:
                        logger.info('<Tecnonews> <_process> Published!')
                        logger.info('<Tecnonews> <_process> \tTitle: %s' % entry.title)
                        logger.info('<Tecnonews> <_process> \tWord_press_url: %s' % wp_url)
                else:
                    self.not_published_in_this_run += 1
                    logger.info("<Tecnonews> <_process> NOT Published (Title: %s)" % entry.title)

                logger.info('<Tecnonews> <_process> <-- FINISHED Publishing logic')

            except Exception as e:
                logger.error("<Tecnonews> <_process> <-- FAILED Rewriting/publishing: %s " % entry.title)
                logger.error("<Tecnonews> <_process> Exception: %s" % e.message)
                logger.error("<Tecnonews> <_process> Traceback: %s" % traceback.format_exc())

        except Exception as e:
            logger.error("<Tecnonews> <_process> <-- FAILED Processing (Title: [%s])" % entry.title)
            logger.error("<Tecnonews> <_process> Exception: %s" % e.message)
            logger.error("<Tecnonews> <_process> Traceback: %s" % traceback.format_exc())

        # Always save
        self.service.save(news_entry=entry)
        logger.info("<Tecnonews> <_process> Saved news entry to DB")

        logger.info("<Tecnonews> <_process> <-- FINISHED processing %s" % entry.title)

    def valid_to_publish(self, rewriter_instance):
        td = TextDistance()
        td.stopwords = []  #avoid using stopwords filter
        clean_rewritten = BeautifulSoup(rewriter_instance.rewritten_entry.content).getText()
        similarity = td.similarity(rewriter_instance.original_entry.content, clean_rewritten)

        logger.info("\nSimilarity %s" % similarity)
        logger_similarity.info("\nSimilarity %s" % similarity)

        # return similarity <= 95
        return rewriter_instance.injected_count > 0

if __name__ == '__main__':
    import argparse
    import time
    from shutil import copyfile

    # TODO: use args and fix synchronization problem when copy config files
    # parser = argparse.ArgumentParser(description='Instantiate NaturalNews.')
    # parser.add_argument('--instance', type=int, nargs=1, help='The instance identification')
    # args = parser.parse_args()
    # config_file = u'instance_config/config_instance_' + unicode(args.instance[0])
    # print config_file

    # copyfile(config_file, 'config')
    # time.sleep(1)
    tn = TecnoNews()
    print "Instance ID: ", tn.config.get('instance', 'id')

    while True:
        if tn.environment_health():
            tn.run()
        else:
            # TODO: must fix the environment somehow
            logger.error("Environment is not healthy - Can't run - Waiting one minute before retrying.")

        logger.info("<Tecnonews> <Main Loop> Sleeping")
        time.sleep(60)
