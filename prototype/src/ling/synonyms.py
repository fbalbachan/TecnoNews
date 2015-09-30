from src.utils.configProvider import ConfigProvider
from _csv import reader

class Synonyms:
    def __init__(self):
        self.replacements = {}
        self.load()

    def load(self):
        config = ConfigProvider()
        replacements_filename = config.get("resources", "synonyms_ext")
        for line in reader(open(replacements_filename, 'r')):
            self.replacements[line[0]] = line[1:len(line)]

#    def get_synonym(self, word):
#        synonym = word
#        if word in self.replacements.keys():
#            synonym = self.synonyms[word][0]
#
#        return synonym

    def get_base_synonym(self, word):
        base_synonym = None
        for base_word, synonym_list in self.replacements.items():
            if word in synonym_list:
                base_synonym = base_word
                break

        return base_synonym
