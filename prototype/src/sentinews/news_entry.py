# -*- coding: utf-8 -*-

from src.sentinews.categorizer import Categorizer
from src.utils.logger_utils import *
from src.utils.configProvider import ConfigProvider
import traceback
import ConfigParser

logger = get_logger('tecnonews')


class NewsEntry(object):
    def __init__(self, title, content, tags, source, url=None, original_categories=None, language=u"spanish",
                 categories=None, wp_id=None, wp_url=None, related=None, entities=None,
                 published_date=None, object_id=None, versions=None, universe_versions=None, universe_scores=None, image=None, image_search_string=None, summary=None):

        self.title = title
        self.content = content
        self.clean_text = None
        self.entities = entities
        self.tags = tags
        self.source = source
        self.original_categories = original_categories
        self.categories = categories
        self.destination = None
        self.published_date = published_date
        self.url = url
        self.wp_id = wp_id
        self.wp_url = wp_url
        self.related = related
        self.object_id = object_id
        self.versions = versions
        self.universe_versions = universe_versions
        self.universe_scores = universe_scores
        self.config = ConfigProvider()
        self.image = image
        self.image_search_string = image_search_string
        self.sentiment = None
        self.countries = []
        self.cities = []
        self.token_count = 0
        self.host_id = None
        self.image_url = None
        self.summary = summary
        self.language = language

        # Defensive programing to avoid wrong encoded
        assert(isinstance(self.title, unicode))
        assert(isinstance(self.content, unicode))

        # 20160328 - Daniel Cantarín
        # There are some problematic titles. Here's some cleaning code.
        self.title = self.title.replace("\n","")

        if self.related is None:
            self.related = []

        if not self.categories:
            self.set_categories()

    def set_categories(self):
        # User must provide some info about original category or tags to have a better
        # category selection. If not we put always the categoty to [u'inter\xe9s general']
        logger.info("alexis news_entry->set_categories")
        if self.original_categories or self.tags:
            merged_tags = []
            if self.original_categories:
                merged_tags += self.original_categories
            if self.tags:
                merged_tags += self.tags

            self.categories = list(Categorizer(merged_tags).get_or_else())

        #logger.info("self.original_categories %s" % self.original_categories)
        #if self.original_categories:
        #    self.categories = list(Categorizer(self.original_categories).get_or_else())
        #    logger.info("Categorizer(self.original_categories)")
        #    logger.info("self.categories %s" % self.categories)

        #if (not self.categories or self.categories == [u'inter\xe9s general']) \
        #        and self.tags:
            # try to find a category using original categories
        #    logger.info("categorization from tags")
        #    self.categories = list(Categorizer(self.tags).get_or_else())

        assert self.categories

        if len(self.categories) == 1 and list(self.categories)[0] == u'inter\xe9s general':
            logger.info("Tags to be categorized")
            logger.info("Original Categories %s " % self.original_categories)
            logger.info("tags %s" % self.tags)
            logger.info("url  %s" % self.url)

    def set_analisys_info(self):
        if not self.clean_text:
            self.clean_text = self.get_clean_text()
        if not self.entities:
            self.entities = self.most_relevant_entities()

    def set_related_news(self, related_news_entries):
        self.related = [entry.object_id for entry in related_news_entries]

    def set_universe_scores(self, universe_scores):
        self.universe_scores = [score for score in universe_scores]

    def set_universe_versions(self, universe_versions):
        self.universe_versions = [entry.object_id for entry in universe_versions if entry.title != self.title]

    def set_news_versions(self, other_versions):
        self.versions = [entry.object_id for entry in other_versions if entry.title != self.title]

    def to_dict(self):
        return dict(title=self.safe_unicode(self.title), content=self.safe_unicode(self.content),
                    tags=self.safe_unicode_list(self.tags), source=self.source,
                    original_categories=self.original_categories, categories=self.categories,
                    entities=self.entities, published_date=self.published_date, url=self.url, wp_id=self.wp_id,
                    wp_url=self.wp_url, related=self.related, versions=self.versions,
                    universe_versions=self.universe_versions, universe_scores=self.universe_scores, sentiment=self.sentiment,
                    countries=self.countries, cities=self.cities,host_id=self.host_id,image_url=self.image_url,
                    summary=self.summary, language=self.language)

    def analyzed_paragraph(self):
        from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
        from src.model.paragraph.paragraph import Paragraph

        analyzer = ParagraphAnalyzer()
        paragraph = Paragraph.from_text(self.safe_str(self.content))
        analyzer.analyze(paragraph)
        return paragraph

    def rank_of_entities(self):
        from src.model.referent.referentRanker import ReferentRanker
        from src.model.referent.entityUnifier import EntityUnifier

        paragraph = self.analyzed_paragraph()
        EntityUnifier(paragraph).unify()
        return ReferentRanker(paragraph).rank()

    def most_relevant_entities(self):
        try:
            ranked_entities_list = self.rank_of_entities()
        except Exception as e:
            logger = get_logger('tecnonews')
            logger.error("<NewsEntry> <most_relevant_entities> %s " % e.message)
            logger.error(traceback.format_exc())
            # If we have an error getting the rank list just return empty relevant entities
            return []

        entities_classification = []
        for entity in ranked_entities_list:
            entities_classification.append({'semantic': entity[0].semantic_classification(),
                                            'name': entity[0].name(), 'score': entity[1]})

        return entities_classification

    def get_clean_text(self):
        return ' '.join([w for w in self.content.split() if w.lower() not in self.load_stopwords()])

    def load_stopwords(self):
        import ConfigParser

        stopwords = []
        config = ConfigProvider()
        stopwords_filename = config.get("resources", "stopwords_es_clean")

        for line in open(stopwords_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                stopwords.append(line.decode('utf-8').rstrip('\n'))

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

    def safe_unicode_list(self, list):
        u_list = []
        for string in list:
            u_list.append(self.safe_unicode(string))

        return u_list

    def safe_str(self, text):
        if isinstance(text, str):
            str_text = text
        else:
            try:
                str_text = text.encode('utf-8')
            except Exception, e:
                logger = get_logger('tecnonews')
                logger.info("NewsEntry safe_str :" + e.message)
                str_text = text

        return str_text
