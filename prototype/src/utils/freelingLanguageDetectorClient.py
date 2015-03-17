#-*- coding: utf-8 -*-
from src.utils.configProvider import ConfigProvider
from src.decorators.singleton import singleton
import re
import subprocess

@singleton
class FreelingLanguageDetectorClient:
    def __init__(self):
        config = ConfigProvider()
        self.config = dict(config.items("freeling_language"))
        self.calls_count = 0

    def health_check(self):
        #TODO: implement
        return True

    def parse(self, text):
        return self.get_client_output_for(text)

    def get_client_output_for(self, text):
        if not isinstance(text, unicode):
            raise Exception("Must provide unicode strings.")

        # TODO: check if
        text = re.sub(r"""[)|(|.|,|"|!|'|@|#|\$|%|^|&|\*]""", ' ', text)

        config = self.config

        p = subprocess.Popen([config["client"], config["host"], config["language_port"]],
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        raw_output = p.communicate(input=text.encode('utf-8'))[0]
        return raw_output.split('\n')

