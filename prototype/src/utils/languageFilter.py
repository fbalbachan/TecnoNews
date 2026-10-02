# -*- coding: utf-8 -*-
from src.utils.languageDetectorClient import LanguageDetectorClient
from src.utils.logger_utils import get_logger


logger = get_logger('tecnonews')


class LanguageFilter(object):

    def __init__(self):
        self.filter = LanguageDetectorClient()

    def only_spanish_paragraph(self, text):

        content_es = ""
        spanish_like_languages = ['es']
        for paragraph in text.split('\n'):
            if paragraph.strip() == '':
                continue

            if self.filter.get_client_output_for(paragraph)[0] \
                    in spanish_like_languages:
                content_es += paragraph.strip() + "\n"
            else:
                logger.info("Is not spanish paragraph:" + paragraph)

        return content_es
