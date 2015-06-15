__author__ = 'Pablo Perez De Angelis'

from src.utils.languageFilter import LanguageFilter
from src.utils.sanitizer import Sanitizer
from src.utils.bit_opener import BitOpener


class GenericParser(object):
    def __init__(self):
        self.language_filter = LanguageFilter()
        self.sanitizer = Sanitizer()
        self.opener = BitOpener()

    def sanitize(self, content):
        return self.sanitizer.process_content(content=content)
