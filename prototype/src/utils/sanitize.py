from src.utils.languageFilter import LanguageFilter
from ConfigParser import ConfigParser


class Sanitizer():

    def __init__(self):
        self.language_filter = LanguageFilter()
        self.config = ConfigParser()
        self.config.read('config')
        self.language_filter_status = self.config.get('language_filter', 'status')
        self.paragraph_to_avoid = self._load_banned_paragraphs()

    def process_content(self, content):

        new_content = '\n'.join([paragraph for paragraph in content.split('\n')
                       if not any(x == paragraph[:len(x)] for x in self.paragraph_to_avoid)])

        if self.language_filter_status == 'ON':
            # Becouse we have a mixed encodes in pipeline be shure it is unicode
            if not isinstance(new_content, unicode):
                new_content = unicode(new_content, 'utf-8')

            new_content = self.language_filter.only_spanish_paragraph(new_content)
        return new_content

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
