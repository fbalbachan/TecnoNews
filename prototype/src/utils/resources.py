# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
# from src.decorators.singleton import singleton

# @singleton
class Resources:
    def __init__(self):
        self.config = None
        self.source_config = None
        self.load_resource_file()

    def load_resource_file(self):
        self.source_config = ConfigParser()
        self.source_config.read("config")

        resources_file = dict(self.source_config.items("resources"))["general_resources"]

        self.config = ConfigParser()
        self.config.read(resources_file)

    def get_config(self, section, key):
        return dict(self.source_config.items(section))[key]

    def get_wordlist(self, section, key):
        _file = open(self.get_config(section, key))
        return [pref.strip("\n") for pref in list(_file)]

    def get_wordlist_safe(self, section, key):
        """
        load resource list of items

        :return: list of unicode words as list
        """
        filename = self.get_config(section, key)
        file_lines = list(open(filename, 'r'))
        items = [self.get_line_item(line) for line in file_lines if self.is_content_line(line)]
        return items

    def is_content_line(self, line):
        is_empty_or_comment = self.is_empty(line) or self.is_comment(line)
        return not is_empty_or_comment

    def is_empty(self, line):
        item = (line.rstrip('\n')).rstrip('\r')
        return len(item) == 0

    def is_comment(self, line):
        return line[0] in ['<', '%']

    def get_line_item(self, line):
        item = (line.rstrip('\n')).rstrip('\r')
        if not isinstance(item, unicode):
            item = unicode(item, 'utf-8')
        return item

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
