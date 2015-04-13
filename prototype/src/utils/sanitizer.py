#-*- coding: utf-8 -*-
import re
from src.decorators.singleton import singleton
from src.utils.languageFilter import LanguageFilter
from src.utils.configProvider import ConfigProvider


@singleton
class Sanitizer():
    def __init__(self):

        self.config = ConfigProvider()
        self.language_filter_status = self.config.get('language_filter', 'status')
        self.paragraph_to_avoid = self._load_banned_paragraphs()
        self.language_filter = None

    def process_content(self, content):
        # We have doubts about the stability of language Filter, so we instanciate each time
        self.language_filter = LanguageFilter()

        # Becouse we have a mixed encodes in pipeline be shure it is unicode
        if not isinstance(content, unicode):
            content = unicode(content, 'utf-8')

        new_content = '\n'.join([paragraph for paragraph in content.split('\n')
                                 if not any(x == paragraph[:len(x)] for x in self.paragraph_to_avoid)])

        if self.language_filter_status == 'ON':
            new_content = self.language_filter.only_spanish_paragraph(new_content)

        new_content = re.sub(u'\(CNN\)', u'', new_content)
        new_content = re.sub(u'\( CNN Español \)', u'', new_content)
        re.sub(r'a EL PAÍS|a EL PAIS',  u'al diario El País de España',
                   new_content, flags=re.UNICODE)

        new_content = re.sub(u', enviad(a|o) especial de euronews\.', u'', new_content)

        new_content = re.sub(r'(La|El) enviad(a|o) especial de euronews(\ a\ la\ zona)?,',
                             u'', new_content)

        new_content = re.sub(u'a CNN', u'al medio estadounidense CNN', new_content)
        new_content = re.sub(u'A CNN', u'Al medio estadounidense CNN', new_content)

        return new_content.strip()

    def _load_banned_paragraphs(self):
        """
        load resource of inital substrings to ignore

        :return: list of initial substrings to ignore in pipeline process
        """
        string_paragraphs = []
        paragraphs_filename = self.config.get("resources", "marks_to_avoid_paragraphs")

        for line in open(paragraphs_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                line_to_add = unicode(line.rstrip('\n'), 'utf-8')
                string_paragraphs.append(line_to_add)

        return string_paragraphs
