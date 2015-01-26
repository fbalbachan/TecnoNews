# -*- coding: utf-8 -*-
from src.utils.freelingLanguageDetectorClient import FreelingLanguageDetectorClient
from src.utils.logger_utils import get_logger

logger = get_logger('tecnonews')


class LanguageFilter(object):
    def __init__(self):
        self.filter = FreelingLanguageDetectorClient()

    def only_spanish_paragraph(self, text):

        content_es = ""
        spanish_like_languages = ['es']
        for paragraph in text.split('\n'):
            if not paragraph == "\n":
                if self.filter.get_client_output_for(paragraph)[0] in spanish_like_languages:
                    content_es += paragraph + "\n"
                else:
                    logger.info("Is not spanish paragraph:" + paragraph)

        return content_es
