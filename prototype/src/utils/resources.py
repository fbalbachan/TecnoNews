#-*- coding: utf-8 -*-
from ConfigParser import ConfigParser


class Resources:
    def __init__(self):
        self.load_resource_file()

    def load_resource_file(self):
        Config = ConfigParser()
        Config.read("config")
        self.source_config = Config

        resources_file = dict(Config.items("resources"))["general_resources"]

        Config =  ConfigParser()
        Config.read(resources_file)
        self.config = Config

    def get_config(self, section, key):
        return dict(self.source_config.items(section))[key]

    def get_wordlist(self, section, key):
        _file = open(self.get_config(section, key))
        return [ pref.strip("\n") for pref in list(_file) ]

    def has_key(self, section, key):
        return key in self.section(section)

    def section(self, section):
        return dict(self.config.items(section))

    def parse_csv_in(self, section, key):
        string = self.section(section)[key]
        values = set()
        for value in string.split(","):
            values.add(value.strip())
        return values

instance = Resources()
