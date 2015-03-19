#-*- coding: utf-8 -*-
#import ConfigParser
from src.utils.configProvider import ConfigProvider
import subprocess


class FreelingClientParser:

    def __init__(self):
        config = ConfigProvider()
        self.config = dict(config.items("freeling"))

    def health_check(self):
        # make a simple consult to validate freeling is responding ok
        expected_result = ['prep_[', '  +(A a SPS00 -)', ']', '', '', '']
        return expected_result == self.parse('A')

    def parse(self, text):
        return self.get_client_output_for(text)

    def get_client_output_for(self, text):
        if type(text) != str: raise Exception("The parse method only accept unicode strings.")

        config = self.config
        p = subprocess.Popen([config["client"], config["host"] + ':' + config["parser_port"]],
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        raw_output = p.communicate(input=text)[0]

        return raw_output.split('\n')

