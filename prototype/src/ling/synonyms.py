# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'

from src.utils.configProvider import ConfigProvider
from _csv import reader


class Synonyms:
    def __init__(self):
        self.replacements = {}
        self.load()

    def load(self):
        config = ConfigProvider()
        replacements_filename = config.get("resources", "synsets")

        resource_line_index = 0
        for line in reader(open(replacements_filename, 'r', encoding="utf-8")):
            for index in range(len(line)):
                if line[index] is None or len(line[index]) == 0:
                    del line[index]
                else:
                    line[index] = line[index].strip(" ")

            if len(line) > 1:
                self.replacements[line[0]] = line[1:len(line)]
            else:
                print("Synsets resource load: Error in line ", resource_line_index, "... skipping.")

            resource_line_index += 1

#    def get_synonym(self, word):
#        synonym = word
#        if word in self.replacements.keys():
#            synonym = self.synonyms[word][0]
#
#        return synonym

    def get_base_synonym(self, word, include_base=False):
        base_synonym = None
        for base_word, synonym_list in list(self.replacements.items()):
            if word in synonym_list:
                base_synonym = base_word
                break
            elif include_base and word == base_word:
                base_synonym = base_word
                break

        return base_synonym
