# -*- coding: utf-8 -*-
import ConfigParser
from src.sentinews.categorizer import Categorizer
from src.sentinews.publisher_host import WPHost
from src.utils.csvwrapper import unicode_csv_reader
from unidecode import unidecode
from datetime import datetime
from src.utils.logger_utils import *
import traceback

'Struct class to contain the news information'


class NewsEntry(object):
    def __init__(self, title, content, tags, source, url=None, categories=None):
        self.title = title
        self.content = content
        self.clean_text = None
        self.entities = None
        self.tags = tags
        self.source = source
        self.categories = categories
        self.destination = None
        self.published_date = datetime.utcnow()
        self.url = url
        self.config = ConfigParser.ConfigParser()
        if self.categories is None:
            self.__setUp()

    def set_analisys_info(self):
        if not self.clean_text:
            self.clean_text = self.get_clean_text()
        if not self.entities:
            self.entities = self.most_relevant_entities()

    def __setUp(self):
        self.config.read('config')
        user_per_categories_file = self.config.get(
            'resources', 'user_per_categories')
        user_per_categories = unicode_csv_reader(open(user_per_categories_file, 'r'),
                                                 first_line_is_header=False, delimiter=',')

        self.user_per_categories_dict = {}
        i = 0
        for row in user_per_categories:
            self.user_per_categories_dict[i] = {}
            self.user_per_categories_dict[i]['user'] = row[1]
            self.user_per_categories_dict[i]['host'] = row[0]
            self.user_per_categories_dict[i]['password'] = row[2]
            self.user_per_categories_dict[i]['categories'] = [
                element for element in row[3:] if element != '']
            i += 1

        self.categories = list(Categorizer(self.tags).get_or_else())
        self.destination = self.__get_hosts(self.categories)


    def __get_hosts(self, categories):
        host_pivot = []
        hosts = set([])
        for category in categories:
            for key in self.user_per_categories_dict:
                for user_category in self.user_per_categories_dict[key]['categories']:
                    if unidecode(user_category.lower()) == unidecode(category.lower()):
                        new_host = WPHost(self.user_per_categories_dict[key]['host'],
                                          self.user_per_categories_dict[key]['user'],
                                          self.user_per_categories_dict[key]['password'])

                        if not (new_host in hosts):
                            hosts.add(new_host)
        return hosts

    def to_dict(self):
        return {'title': self.safe_unicode(self.title),
                'content': self.safe_unicode(self.content),
                'tags': self.safe_unicode_list(self.tags),
                'source': self.source, 'categories': self.categories,
                'entities': self.entities,
                'published_date': self.published_date, 'url': self.url}

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
        except Exception, e:
            logger = get_logger('tecnonews')
            logger.error("NewsEntry most_relevant_entities :" + e.message)
            logger.error("NewsEntry most_relevant_entities :" + traceback.format_exc())
            # If we have an error geting the rank list just return empty relevant entities
            return []

        entities_classification = []
        for entity in ranked_entities_list:
            entities_classification.append({'semantic': entity[0].semantic_classification(),
                                            'name': entity[0].name(), 'score': entity[1]})

        return entities_classification

    def get_clean_text(self):
        return ' '.join([w for w in self.content.split() if w not in self.load_stopwords()])

    def load_stopwords(self):
        import ConfigParser

        stopwords = []
        config = ConfigParser.ConfigParser()
        config.read("config")

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
