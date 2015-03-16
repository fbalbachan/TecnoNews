__author__ = 'Pablo Perez De Angelis'
from src.utils.textDistance import TextDistance
from src.utils.configProvider import ConfigProvider

class NewsItem(object):

    def __init__(self, file_name, content, title):
        self.file_name = file_name
        self.content = content

        self.paragraph = self.analyzed_paragraph()

        self.title = title
        self.title_lemmatized = ''
        # self.content_lemmatized = self.lemmatized_content()
        self.entities = self.most_relevant_entities()
        self.clean_text = self.get_clean_text()
        # self.clean_content_lemmatized = self.get_cleaned_content_lemmatized()
        self.paragraph = ''


    @classmethod
    def from_file(cls, path, file_name):
        content = open(path + file_name, 'r').read()
        title = open(path + file_name, 'r').readline()

        return cls(file_name, content, title)

    def analyzed_paragraph(self):
        from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
        from src.model.paragraph.paragraph import Paragraph

        analyzer = ParagraphAnalyzer()
        paragraph = Paragraph.from_text(self.content)
        analyzer.analyze(paragraph)
        return paragraph

    # TODO: move this outside when this goes to production and
    def rank_of_entities(self):
        from src.model.referent.referentRanker import ReferentRanker
        # from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
        # from src.model.paragraph.paragraph import Paragraph
        from src.model.referent.entityUnifier import EntityUnifier

        # analyzer = ParagraphAnalyzer()
        # paragraph = Paragraph.from_text(text)
        # analyzer.analyze(paragraph)
        paragraph = self.paragraph
        EntityUnifier(paragraph).unify()
        return ReferentRanker(paragraph).rank()

    def most_relevant_entities(self):
        ranked_entities_list = self.rank_of_entities()
        entities_classification = []

        for entity in ranked_entities_list:
            entities_classification.append({'semantic': entity[0].semantic_classification(),
             'name': entity[0].name(), 'score': entity[1]})

        return entities_classification


    def lemmatized_content(self):
        lemmatized = ''
        for sentence in self.paragraph.sentences:
            for leaf in sentence.parse_node.leaves():
                lemmatized += ' ' + leaf.lemma

        return lemmatized

    def get_clean_text(self):
        # Use TextDistance pre processing to clean the text
        td = TextDistance()
        return td.pre_process(self.content)

    def load_stopwords(self):
        stopwords = []
        config = ConfigProvider()

        stopwords_filename = config.get("resources", "stopwords_es_clean")

        for line in open(stopwords_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                stopwords.append(line.rstrip('\n'))

        return stopwords

    def get_cleaned_content_lemmatized(self):
        return ' '.join([w for w in self.content_lemmatized.split() if w not in self.load_stopwords()])