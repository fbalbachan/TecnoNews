# -*- coding: utf-8 -*-
from src.utils.textDistance import TextDistance
from src.utils.configProvider import ConfigProvider
from src.services.mongodb.news_entries_service import NewsEntriesService
from datetime import datetime, timedelta

class RacontoFinder(object):
    def __init__(self, original):
        default_from = 30
        default_to = 7

        special_limits = [
            {"category":u"tecnología", "limit":10},
            {"category":u"belleza", "limit":30},
            {"category":u"propiedades", "limit":30},
            {"category":u"electrodomésticos", "limit":30},
            {"category":u"automóviles", "limit":30},
            {"category":u"turismo", "limit":30},
            {"category":u"estilo vida", "limit":30},
            {"category":u"salud", "limit":30},
            {"category":u"zolvers", "limit":30},
        ]

        self.news_original = original
        self.news_to_compare = []

        for a_limit in special_limits:
            if a_limit["category"] in self.news_original.categories and a_limit["limit"] > default_to:
                default_to = a_limit["limit"] + 1
                default_from = a_limit["limit"] + 30

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

    def set_best_raconto(self):
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

        if len(final_result) > 0:
            selected_best = final_result[0]
            for a_final in final_result:
                if a_final[1] > selected_best[1]:
                    selected_best = a_final
                elif a_final[1] == selected_best[1]:
                    if a_final[0].object_id.generation_time > selected_best[0].object_id.generation_time:
                        selected_best = a_final
            self.format_raconto(selected_best[0])
            return selected_best[0]
        else:
            return None

    def format_raconto(self, raconto):
        self.news_original.raconto_content = raconto.content.split()[0]
        self.news_original.raconto_title = raconto.title
        self.news_original.raconto_date = raconto.object_id.generation_time
        self.news_original.raconto_id = raconto.object_id

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
