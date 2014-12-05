#-*- coding: utf-8 -*-
import os, ConfigParser


class FreelingLanguageDetectorClient:
    def parse(self, text):
        return self.get_client_output_for(text)

    def get_client_output_for(self, text):
        if type(text) != str: raise Exception("Solo se acepta unicode codificado a string.")
        # text = text.replace('"', '\\"')

        config = self.config

        command = "echo '%s'" + ' | ' + config["client"] + ' ' + config["host"] + ' ' + config["language_port"]

        raw_output = os.popen((command % text)).read()
        return raw_output.split('\n')

    def setup_config(self):
        Config = ConfigParser.ConfigParser()
        Config.read("config")
        self.config = dict(Config.items("freeling_language"))

    def __init__(self):
        self.setup_config()
