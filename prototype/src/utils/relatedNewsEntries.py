# -*- coding:utf-8 -*-
from src.utils.textDistance import TextDistance
from src.sentinews.news_entry import NewsEntry
import ConfigParser


class RelatedNewsEntries(object):
    def __init__(self, original, to_compare_news_entries):
        self.news_original = original
        self.news_to_compare = to_compare_news_entries
        self.text_distance = TextDistance()
        self.stopwords = self.load_stopwords()

        #
        self.pre_process(self.news_original)
        for news in self.news_to_compare:
            self.pre_process(news)

    def load_stopwords(self):
        stopwords = []
        config = ConfigParser.ConfigParser()
        config.read("config")

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
                logger = get_logger('tecnonews')
                logger.info("NewsEntry safe_unicode :" + e.message)
                u_text = text

        return u_text

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
            cleaned_title = ' '.join([w for w in newsItem.title.split() if w not in self.stopwords])
            similarity = self.text_distance.title_distance(cleaned_original_title, cleaned_title)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)



    def get_related(self):
        original = self.news_original

        # print "\n"
        # print "Title distance:", original.title
        #
        # for result in tsr.get_title_distance_rank():
        #     if float(result[0]) < 0.9:
        #         print result[0], result[1].url

        # print "\n"
        # print "similarity lemmatized filename original:", original_file
        # for result in tsr.get_similarity_rank_content_lemmatized():
        #     print result[0], result[1].url
        #
        # print "\n"
        # print "similarity original:", original.title
        #
        # for result in tsr.get_similarity_rank():
        #     if float(result[0]) > 20.0:
        #         print result[0], result[1].url


        # print "\n"
        # print "similarity filename original WO stopwords lemmatized:", original_file
        #
        # for result in tsr.get_similarity_rank_clean_content_lemmatized():
        #     print result[0], result[1].url

        for result in tsr.get_similarity_rank_entities():
            if result[0] > 1:
                logger.info("%s %s %s" % (result[0], result[1].url, result[1].title))
            else:
                self.news_to_compare.remove(result[1])

        # logger.info("similarity original WO stopwords")

        for result in tsr.get_similarity_rank_cleaned():
            if float(result[0]) > 20.0:
                logger.info("%s %s %s" % (result[0], result[1].url, result[1].title))
            else:
                self.news_to_compare.remove(result[1])

        logger.info("Title distance cleaned: %s" % original.title)
        for result in tsr.get_title_distance_rank():
            if float(result[0]) <= 0.9:
                logger.info("%s %s %s" % (result[0], result[1].url, result[1].title))
            else:
                self.news_to_compare.remove(result[1])

        logger.info("Original\n %s - %s %s" % (original.source, original.title, original.categories))
        logger.info("\nrelated articles from different source:")


        if len(self.news_to_compare) > 0:
            for result in self.news_to_compare:
                if self.safe_unicode(original.source) != self.safe_unicode(result.source):
                    logger.info("\t With different source")
                    logger.error("\t>>> %s %s" %  (result.url, result.title))
        else:
            logger.info("No one")


    def get_related_human_frendly(self):

        final_result = []
        cleaned_original_title = ' '.join([w for w in self.news_original.title.split() if w not in self.stopwords])

        for newsItem in self.news_to_compare:
            logger.info("\ncase comparing to:")
            logger.info("\t%s" % newsItem.title)
            logger.info("\t%s\n" % newsItem.url)
            logger.info("\tmetrics:")
            entities_coincidence = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            logger.info("\t\tEntities coincidence %s" % entities_coincidence)
            similarity = self.text_distance.similarity(self.news_original.clean_text, newsItem.clean_text)
            logger.info("\t\tContet Similarity %s" % similarity)

            cleaned_title = ' '.join([w for w in newsItem.title.split() if w not in self.stopwords])
            title_distance = self.text_distance.title_distance(cleaned_original_title, cleaned_title)

            logger.info("\t\tTitle Distance %s" % title_distance)

            score = 0
            if entities_coincidence > 1:
                score += 30

            if title_distance <= 0.9:
                score += 20

            if 5.0 <= similarity < 30:
                score += 10
            elif 30.0 <= similarity < 50:
                score += 30
            elif 50.0 <= similarity <= 100:
                score += 50

            if score >= 40:
                logger.info(">>>")
                final_result.append(newsItem)

            logger.info("\t\tscore: %s" % score)

        logger.info("---\n")


def save_test_data(original, to_compare):
    import pickle

    with open('original.pkl', 'wb') as output:
        pickle.dump(original, output, pickle.HIGHEST_PROTOCOL)

    with open('to_compare.pkl', 'wb') as output:
        pickle.dump(to_compare, output, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    from src.services.mongodb.news_entries_service import NewsEntriesService
    import logging
    # from __future__ import print_function

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler('related.log', 'a'))

    nes = NewsEntriesService()

    news_to_compare = nes.get_last_n_days(1, ['internacionales'])

    logger.info("Total Cases: %i" % len(news_to_compare))
    for ntc in news_to_compare:
        if not ntc.url:
            continue
            
        logger.info("---------------")
        original = ntc
        logger.info("case: %s" % original.url)
        logger.info("title: %s" % original.title)

        # Find all in the same category in the last 5 days with different url
        news_to_compare = nes.get_last_n_days(1, original.categories, original.url, base_date=original.published_date)

        logger.info("Comparing to %s articles" % len(news_to_compare))
        # print "len", len(news_to_compare)
        tsr = RelatedNewsEntries(original, news_to_compare)

        tsr.get_related_human_frendly()

        logger.info("---------------")
