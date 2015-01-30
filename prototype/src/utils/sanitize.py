from src.utils.languageFilter import LanguageFilter
from ConfigParser import ConfigParser


class Sanitizer():

    def __init__(self):
        self.language_filter = LanguageFilter()
        config = ConfigParser()
        config.read('config')
        self.language_filter_status = config.get('language_filter', 'status')


	def process_content(self, content):
		new_content = content
		if self.language_filter_status == 'ON':
			new_content = self.language_filter.only_spanish_paragraph(content.encode("utf-8"))
		return new_content