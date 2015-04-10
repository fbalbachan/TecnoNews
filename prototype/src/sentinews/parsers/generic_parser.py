__author__ = 'Pablo Perez De Angelis'

from src.utils.languageFilter import LanguageFilter
from src.utils.sanitizer import Sanitizer


class GenericParser(object):
    def __init__(self):
        self.language_filter = LanguageFilter()
        self.sanitizer = Sanitizer()

    def sanitize(self, content):
        return self.sanitizer.process_content(content=content)
