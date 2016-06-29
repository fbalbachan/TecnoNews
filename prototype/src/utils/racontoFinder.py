# -*- coding: utf-8 -*-
from src.utils.textDistance import TextDistance
from src.utils.configProvider import ConfigProvider
from src.services.mongodb.news_entries_service import NewsEntriesService
from datetime import datetime, timedelta

class RacontoFinder(object):
    def __init__(self, original):
        default_from = 30
        default_to = 7
        self.news_original = original
        self.news_to_compare = []

        self.text_distance = TextDistance()
        self.stopwords = self.load_stopwords()
        self.load_news_entries(timedelta_from=default_from, timedelta_to=default_to)
        for news in self.news_to_compare:
            news.clean_text = ' '.join([w for w in news.content.split() if w not in self.stopwords])

    def load_news_entries(self, timedelta_from, timedelta_to):
        nes = NewsEntriesService()
        fromDate = datetime.utcnow() - timedelta(days=timedelta_from)
        toDate = datetime.utcnow() - timedelta(days=timedelta_to)
        self.news_to_compare = nes.get_by_categories_date_range(
                                                            fromDate=fromDate,
                                                            toDate=toDate,
                                                            categories=self.news_original.categories)

    def get_best_raconto(self):
        final_result = []
        for newsItem in self.news_to_compare:
            entities_coincidence_5 = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem)
            entities_coincidence_3 = self.text_distance.relevant_entities_coincidence(self.news_original, newsItem, stopAt=3)
            similarity = self.text_distance.similarity(self.news_original.clean_text, newsItem.clean_text)
            title_distance = self.text_distance.title_distance(self.news_original.title, newsItem.title)

            threshold = 40
            score = self.related_score(entities_coincidence_5, entities_coincidence_3, similarity, title_distance)
            if score >= threshold:
                final_result.append([newsItem, score])

        sorted_final = sorted(final_result, key=lambda x: x[1], reverse=True)

        earliest = datetime.utcnow()
        final_return = None
        for a_final in sorted_final:
            if a_final[0].object_id.generation_time < earliest:
                final_return = a_final[0]

        return final_return

    def related_score(self, entities_coincidence_5, entities_coincidence_3, similarity, title_distance):
        score = 0

        if entities_coincidence_5 > 1 or entities_coincidence_3 > 0:
            score += 30

            if 0.6 < title_distance <= 0.95:
                score += 20
            elif title_distance <= 0.6:
                score += 30

            if 5.0 <= similarity < 10:
                score += 10
            elif 10.0 <= similarity < 30:
                score += 30
            elif 30.0 <= similarity <= 100:
                score += 50

        return score

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
