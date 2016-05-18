# -*- coding: utf-8 -*-
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
import traceback
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

    def _environment_health(self):
        li_health = self.freeling_lang_ident.health_check()
        parse_health = self.freeling_parse.health_check()

        return li_health and parse_health

    def run(self):
        logger = get_logger('tecnonews')
        logger.info("<Tecnonews> <run> Running start")
        self.published_in_this_run = 0
        self.not_published_in_this_run = 0

        entries = NewsCrawler().crawl_all()

        logger.info("<Tecnonews> <run> Entries to publish: %s" % len(entries))

        for idx, entry in enumerate(entries):
            logger.info("<Tecnonews> <run> processing entry %s of %s" % (idx, len(entries)))
            self._process(entry)

        logger.info("Freeling ident calls number:%s" % self.freeling_lang_ident.calls_count)
        logger.info("not published: %s \n Published: %s" % (self.not_published_in_this_run,
                                                            self.published_in_this_run))
        logger.info("<Tecnonews> <run> Done.")

    def _process(self, entry):
        logger.info("<Tecnonews> <_process> START processing %s" % entry.title)
        other_versions = []
        try:
            entry.set_analisys_info()
            try:
                tsr = RelatedNewsEntries(entry)
                tsr_universe = RelatedNewsEntries(entry, for_universe=True)

                other_versions = tsr.get_other_versions_top_ten()
                other_versions = [entry_version for entry_version in other_versions if entry_version.title != entry.title]
                universe_versions_scored = tsr_universe.get_other_versions(with_score=True)
                related = tsr.get_related_entities_top_5_not_in_list(other_versions)

                entry.set_news_versions(other_versions)
                entry.set_universe_versions([x[0] for x in universe_versions_scored])
                entry.set_universe_scores([x[1] for x in universe_versions_scored])
                entry.set_related_news(related)

                logger.info("<Tecnonews> <_process> same news different coverage number %s" % len(other_versions))
                logger.info("<Tecnonews> <_process> related_news number %s" % len(related))
            except Exception as e:
                logger.error("<Tecnonews> <_process> related_news %s" % entry.title)
                logger.error("<Tecnonews> <_process> related_news %s" % str(e))
                logger.error("<Tecnonews> <_process> related_news %s" % traceback.format_exc())
                logger.info(traceback.format_exc())

            rewriter = NewsRewriter(entry)
            # Add the other_version entries (only ids) to be used in paragraph insertion
            rewriter.rewritten_entry.other_versions = other_versions

            logger.info('<Tecnonews> <_process> rewriting note: ' + entry.title)
            try:
                rewriter.rewrite_title()
                rewriter.rewrite_content()

                #entry.sentiment = rewriter.original_entry.sentiment

                logger_similarity.info("\n--------\n")
                logger_similarity.info("url: %s\n" % rewriter.original_entry.url)
                logger_similarity.info("Original content")
                logger_similarity.info("%s" % rewriter.original_entry.content)
                logger_similarity.info("Rewritten content")
                clean_rewrited = BeautifulSoup(rewriter.rewritten_entry.content).getText()
                logger_similarity.info("%s" % clean_rewrited)

                valid_to_publish = self.valid_to_publish(rewriter)

                logger_similarity.info("\n\nvalid to publish %s " % valid_to_publish)
                logger_similarity.info("\n--------\n")

                entry.published_date = datetime.utcnow()

                if valid_to_publish:
                    logger.info('<Tecnonews> <_process> publishing: ' + entry.title)
                    wp_id, wp_url, host_id, image_url = rewriter.publish()
                    entry.wp_id = wp_id
                    entry.wp_url = wp_url

                    entry.host_id = host_id
                    entry.image_url = image_url
                    if wp_id:
                        logger.info('<Tecnonews> <_process> published %s' % wp_url)
                    # TODO: check if we must use datetime from wp
                    #entry.published_date = datetime.utcnow()
                    self.published_in_this_run += 1
                else:
                    self.not_published_in_this_run += 1
                    logger.info("Not publishing")

            except Exception as e:
                logger.error("<Tecnonews> <_process> rewriting fail: %s " % entry.title)
                logger.error("%s" % str(e))
                logger.error(traceback.format_exc())

        except Exception as e:
            logger.info(traceback.format_exc())
            logger.error("%s" % str(e))

        # Always save
        self.service.save(news_entry=entry)

        logger.info("<Tecnonews> <_process> END processing %s" % entry.title)

    def valid_to_publish(self, rewriter_instance):
        td = TextDistance()
        td.stopwords = []  #avoid using stopwords filter
        clean_rewrited = BeautifulSoup(rewriter_instance.rewritten_entry.content).getText()
        similarity = td.similarity(rewriter_instance.original_entry.content,
                                   clean_rewrited)

        logger.info("\nsimilarity %s" % similarity)
        logger_similarity.info("\nsimilarity %s" % similarity)

        # return similarity <= 95
        return rewriter_instance.injected_count > 0 and len(clean_rewrited) >= 300

if __name__ == '__main__':
    # import argparse
    import time
    # from shutil import copyfile
    # TODO: use args and fix synchronization problem when copy config files
    # parser = argparse.ArgumentParser(description='Instantiate instance of NaturalNews.')
    # parser.add_argument('--instance', type=int, nargs=1,
    #                help='The instance identification')
    # args = parser.parse_args()
    # config_file = u'instance_config/config_instance_' + unicode(args.instance[0])
    # print config_file

    # copyfile(config_file, 'config')
    # time.sleep(1)
    tn = TecnoNews()
    instance_id = tn.config.get('instance', 'id')
    print instance_id

    while True:
        if tn._environment_health():
            tn.run()
        else:
            #TODO: must fix the environment somehow
            logger.error("Not running because environment is not health")

        logger.info("Sleeping")
        time.sleep(60)
