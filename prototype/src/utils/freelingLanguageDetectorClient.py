#-*- coding: utf-8 -*-
import ConfigParser
import re
import subprocess


class FreelingLanguageDetectorClient:
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

    def setup_config(self):
        Config = ConfigParser.ConfigParser()
        Config.read("config")
        self.config = dict(Config.items("freeling_language"))

    def __init__(self):
        self.setup_config()
