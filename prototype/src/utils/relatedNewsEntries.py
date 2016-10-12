# -*- coding:utf-8 -*-
__author__ = 'Pablo Perez De Angelis'
from src.utils.textDistance import TextDistance
from src.utils.configProvider import ConfigProvider
from src.utils.logger_utils import *
from datetime import datetime, timedelta
from src.services.mongodb.news_entries_service import NewsEntriesService

related_logger = get_logger('tecnonews')

class RelatedNewsEntries(object):

    def __init__(self, original, to_compare_news_entries=None, for_universe=False, optimized=False):
        DAYS_IN_THE_PAST_TO_SEARCH = 5 #number of days to search

        #NEW METHOD (FOR VERSIONS_UNIVERSE)
        special_limits = [
            {"category":u"deporte", "limit":3},
            {"category":u"tecnología", "limit":10},
            {"category":u"mujer", "limit":30},
            {"category":u"propiedades", "limit":30},
            {"category":u"electrodomésticos", "limit":30},
            {"category":u"automóviles", "limit":30},
            {"category":u"turismo", "limit":30},
            {"category":u"estilo vida", "limit":30},
            {"category":u"salud", "limit":30},
            {"category":u"zolvers", "limit":30},
        ]


        default_limit = 5
        minimum_limit = 10000
        for a_limit in special_limits:
            if a_limit["category"] in original.categories:
                if a_limit["limit"] < minimum_limit:
                    minimum_limit = a_limit["limit"]
            else:
                if default_limit < minimum_limit:
                    minimum_limit = default_limit

        #FAILSAFE:
        if minimum_limit == 10000:
            minimum_limit = default_limit


        #OLD METHOD (FOR VERSIONS):
        if u"propiedades" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"electrodomésticos" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"automóviles" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"turismo" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"estilo vida" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"tecnología" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 10

        if u"mujer" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"deporte" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 3

        if u"salud" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        if u"zolvers" in original.categories:
            DAYS_IN_THE_PAST_TO_SEARCH = 30

        #if u"turismo" in original.categories and not u"tecnología" in original.categories:
        #    DAYS_IN_THE_PAST_TO_SEARCH = 30

        self.news_original = original
        self.for_universe = for_universe
        if for_universe:
            self.time_from = datetime.utcnow() - timedelta(days=minimum_limit)
        else:
            self.time_from = datetime.utcnow() - timedelta(days=DAYS_IN_THE_PAST_TO_SEARCH)
        self.time_to = datetime.utcnow()

        if to_compare_news_entries is None and not optimized:
            if for_universe:
                self.load_news_entries(days=minimum_limit, for_universe=for_universe)
            else:
                self.load_news_entries(days=DAYS_IN_THE_PAST_TO_SEARCH)
        else:
            self.news_to_compare = to_compare_news_entries
        self.text_distance = TextDistance()
        self.stopwords = self.load_stopwords()

        #
        self.pre_process(self.news_original)

        if not optimized:
            for news in self.news_to_compare:
                self.pre_process(news)

        # self.get_logger()

    @staticmethod
    def get_logger():
        global related_logger
        if not related_logger:
            import logging
            from logging.handlers import RotatingFileHandler
            import logging.handlers

            logging.basicConfig(level=logging.INFO, format='%(message)s')

            logger = logging.getLogger('Related News')
            logger.addHandler(RotatingFileHandler('logs/related.log', 'a',
                maxBytes=5000000, backupCount=50))
            logger.addHandler(logging.StreamHandler())
            logger.propagate = False
            related_logger = logger
        return related_logger

    def load_stopwords(self):
        stopwords = []
        config = ConfigProvider()

        stopwords_filename = config.get("resources", "stopwords_es_clean")

        for line in open(stopwords_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                stopwords.append(self.safe_unicode(line.rstrip('\n')))

        return stopwords

    def safe_unicode(self, text):
        if isinstance(text, unicode):
            u_text = text
        else:
            try:
                u_text = unicode(text, 'utf-8', errors='ignore')
            except Exception, e:
                u_text = text

        return u_text

    def load_news_entries(self, days, for_universe=False):
        nes = NewsEntriesService()

        fromDate = datetime.utcnow() - timedelta(days=days)
        toDate = datetime.utcnow()

        if for_universe:
            news_to_compare = nes.get_by_id_date_range(fromDate=fromDate, toDate=toDate)
        else:
            news_to_compare = nes.get_by_categories_date_range(fromDate=fromDate, toDate=toDate,
                                                           categories=self.news_original.categories)

        self.news_to_compare = news_to_compare

    def pre_process(self, news_entry):
        if not news_entry.clean_text:
            news_entry.clean_text = ' '.join([w for w in news_entry.content.split() if w not in self.stopwords])

    def get_similarity_rank(self):
        return self.get_similarity_rank_original()

    def get_similarity_rank_entities(self):
        similarities = []
        for newsItem in self.news_to_compare:
            similarity = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_related_entities_top_5_not_in_list(self, same_news):
        same_news_ids = [enty.object_id for enty in same_news]
        related = [] #Array of ids
        for newsItem in self.news_to_compare:
            coincidence = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            if coincidence >= 2 and newsItem.object_id not in same_news_ids:
                related.append([coincidence, newsItem])

        sorted_related_top5 = sorted(related, key=lambda x: x[0], reverse=True)[:5]
        return [x[1] for x in sorted_related_top5]

    def get_similarity_rank_original(self):
        similarities = []

        for newsEntry in self.news_to_compare:
            similarity = self.text_distance.similarity(self.news_original.content, newsEntry.content)
            similarities.append([similarity, newsEntry])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_content_lemmatized(self):
        similarities = []

        for newsEntry in self.news_to_compare:
            similarity = self.text_distance.similarity(self.news_original.content_lemmatized,
                                                       newsEntry.content_lemmatized)
            similarities.append([similarity, newsEntry])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_clean_content_lemmatized(self):
        similarities = []

        for newsItem in self.news_to_compare:
            similarity = self.text_distance.similarity(self.news_original.clean_content_lemmatized,
                                                       newsItem.clean_content_lemmatized)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_cleaned(self):
        similarities = []

        for newsItem in self.news_to_compare:
            similarity = self.text_distance.similarity(self.news_original.clean_text, newsItem.clean_text)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_title_distance_rank(self):
        similarities = []

        for newsItem in self.news_to_compare:
            similarity = self.text_distance.title_distance(self.news_original.title, newsItem.title)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_title_distance_rank_cleaned(self):
        similarities = []
        cleaned_original_title = ' '.join([w for w in self.news_original.title.split() if w not in self.stopwords])
        for newsItem in self.news_to_compare:
            cleaned_title = ' '.join([w.lower() for w in newsItem.title.split() if w not in self.stopwords])
            similarity = self.text_distance.title_distance(cleaned_original_title, cleaned_title)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_other_versions_top_ten(self):
        other_versions = self.get_other_versions()
        return other_versions[:10]

    def get_other_versions_optimized(self, with_score=False):
        related_logger.info("\ntitle: %s" % self.news_original.title)

        nes = NewsEntriesService()
        entries_iterable = None
        if not self.for_universe:
            entries_iterable = nes.get_by_categories_date_range(self.time_from, self.time_to, self.news_original.categories, get_iterable=True,  projection={'_id': 1, 'url':1, 'content':1, 'title':1, 'entities':1})
        else:
            entries_iterable = nes.get_by_id_date_range(self.time_from, self.time_to, get_iterable=True, projection={'_id': 1, 'url':1, 'content':1, 'title':1, 'entities':1})

        final_result = []
        threshold = 40

        has_next = True
        while has_next:
            newsItem = entries_iterable.next()
            has_next = newsItem is not None
            if not has_next:
                continue

            related_logger.info("\ncase comparing to:")
            related_logger.info("\t%s" % newsItem.title)
            related_logger.info("\t%s\n" % newsItem.url)

            score = 0

            if not newsItem.url or newsItem.url == self.news_original.url:
                continue

            entities_coincidence = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            title_distance = self.text_distance.title_distance(self.news_original.title, newsItem.title)

            related_logger.info("\t\tEntities coincidence %s" % entities_coincidence)
            related_logger.info("\t\tTitle Distance %s" % title_distance)

            #-------------SCORING--------------
            if any(special_cat in self.news_original.categories for special_cat in [u"electrodomésticos", "propiedades"]):
                if entities_coincidence >= 1:
                    score += 30
            else:
                if entities_coincidence > 1:
                    score += 30

            if u"propiedades" in self.news_original.categories:
                if 0.7 < title_distance <= 0.95:
                    score += 20
                elif title_distance <= 0.7:
                    score += 30
            else:
                if 0.6 < title_distance <= 0.95:
                    score += 20
                elif title_distance <= 0.6:
                    score += 30

            if score == 0:
                continue

            newsItem.clean_text = ' '.join([w for w in newsItem.content.split() if w not in self.stopwords])
            similarity = self.text_distance.similarity(self.news_original.clean_text, newsItem.clean_text)


            if 5.0 <= similarity < 10:
                score += 10
            elif 10.0 <= similarity < 30:
                score += 30
            elif 30.0 <= similarity <= 100:
                #score += 50
                score = 0 #PROBABLEMENTE SEA CONTENIDO IDENTICO!

            if score >= threshold:
                final_result.append([newsItem, score])
                related_logger.info("%s %s" % (newsItem.title, score))

        sorted_final = sorted(final_result, key=lambda x: x[1], reverse=True)
        if with_score:
            return sorted_final
        else:
            return [x[0] for x in sorted_final]


    def get_other_versions(self, with_score=False):

        final_result = []

        related_logger.info("---------------")
        related_logger.info("case: %s" % self.news_original.url)
        related_logger.info("title: %s" % self.news_original.title)
        related_logger.info("Number of news to search for a related: %s" % len(self.news_to_compare))

        for newsItem in self.news_to_compare:
            if not newsItem.url or newsItem.url == self.news_original.url:
                continue

            related_logger.info("\ntitle: %s" % self.news_original.title)
            related_logger.info("\ncase comparing to:")
            related_logger.info("\t%s" % newsItem.title)
            related_logger.info("\t%s\n" % newsItem.url)
            related_logger.info("\tmetrics:")

            entities_coincidence = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            #entities_coincidence_2 = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem, stopAt=2)
            related_logger.info("\t\tEntities coincidence %s" % entities_coincidence)

            similarity = self.text_distance.similarity(self.news_original.clean_text, newsItem.clean_text)
            related_logger.info("\t\tContent Similarity %s" % similarity)

            title_distance = self.text_distance.title_distance(self.news_original.title, newsItem.title)

            related_logger.info("\t\tTitle Distance %s" % title_distance)

            score = self.related_score(entities_coincidence, similarity, title_distance)

            threshold = 40
            if any(special_cat in self.news_original.categories for special_cat in [u"belleza", u"estilo vida", u"propiedades", u"salud", u"zolvers"]):
                threshold = 40

            if score >= threshold:
                related_logger.info(">>>")
                final_result.append([newsItem, score])
                related_logger.info("%s %s" % (newsItem.title, score))

            related_logger.info("\t\tscore: %s" % score)

        related_logger.info("asociated :")
        for r in final_result:
            related_logger.info("%s %s" % (r[0].title, r[1]))

        related_logger.info("---------------")
        sorted_final = sorted(final_result, key=lambda x: x[1], reverse=True)

        if with_score:
            return sorted_final
        else:
            return [x[0] for x in sorted_final]

    def related_score(self, entities_coincidence, similarity, title_distance):
        score = 0

        related_logger.info("Alexis alexis score related news")
        #if u"propiedades" in self.news_original.categories or u"turismo" in self.news_original.categories: # or u"insólito" in self.news_original.categories:
        if any(special_cat in self.news_original.categories for special_cat in [u"electrodomésticos", "propiedades"]):
            if entities_coincidence >= 1:
                score += 30
        else:
            if entities_coincidence > 1:
                score += 30

        #if entities_coincidence > 1:
        #    score += 30

        if u"propiedades" in self.news_original.categories:
            if 0.7 < title_distance <= 0.95:
                score += 20
            elif title_distance <= 0.7:
                score += 30
        else:
            if 0.6 < title_distance <= 0.95:
                score += 20
            elif title_distance <= 0.6:
                score += 30

        if 5.0 <= similarity < 10:
            score += 10
        elif 10.0 <= similarity < 30:
            score += 30
        #elif 30.0 <= similarity <= 100:
        #    score += 50

        return score

def save_test_data(original, to_compare):
    import pickle

    with open('original.pkl', 'wb') as output:
        pickle.dump(original, output, pickle.HIGHEST_PROTOCOL)

    with open('to_compare.pkl', 'wb') as output:
        pickle.dump(to_compare, output, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    from src.services.mongodb.news_entries_service import NewsEntriesService
    from datetime import datetime, timedelta
    import logging
    # from __future__ import print_function

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger('Related News')
    logger.addHandler(logging.FileHandler('related.log', 'a'))

    fromDate = datetime.now() - timedelta(days=1)
    toDate = datetime.now()

    nes = NewsEntriesService()
    news_to_compare = nes.get_by_categories_date_range(fromDate=fromDate, toDate=toDate,
                                                       categories=['internacionales'])

    logger.info("Total Cases: %i" % len(news_to_compare))
    for ntc in news_to_compare:
        if not ntc.url:
            continue

        logger.info("---------------")
        original = ntc
        logger.info("case: %s" % original.url)
        logger.info("title: %s" % original.title)

        tsr = RelatedNewsEntries(original)

        tsr.get_other_versions()
        # tsr.get_similarity_rank_cleaned()
        logger.info("---------------")
