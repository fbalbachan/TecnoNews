#-*- coding: utf-8 -*-
from ConfigParser import ConfigParser


class Resources:
    def __init__(self):
        self.load_resource_file()

    def load_resource_file(self):
        Config = ConfigParser()
        Config.read("config")
        resources_file = dict(Config.items("resources"))["general_resources"]

        Config.read(resources_file)
        self.config = Config

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
