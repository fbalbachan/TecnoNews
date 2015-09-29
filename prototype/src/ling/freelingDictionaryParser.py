# -*- coding: utf-8 -*-
from src.ling.msi_mapper import tag_to_full_msi
from src.ontology.lexicalForm import LexicalForm
from src.ontology.ontology import Ontology
from src.utils.resources import instance as resources

class FreelingDictionaryParser:

    _ontology = None

    def __init__(self):
        pass

    def get_ontology(self):

        if not FreelingDictionaryParser._ontology:
            FreelingDictionaryParser._ontology = FreelingDictionaryParser.from_resource()

        return FreelingDictionaryParser._ontology

    def parse_ontology(self, _file, ontology_name):
        ontology = Ontology(ontology_name)
        for line in open(_file):
            tokens = line.strip().split()

            lexical_form = tokens[0]

            lemmas = tokens[1::2]
            tags = tokens[2::2]

            for lemma, tag in zip(lemmas, tags):
                try:
                    if "+" in lemma:
                        continue
                    full_msi = tag_to_full_msi(tag)
                    full_lexical_form =LexicalForm(lexical_form, full_msi, lemma, None)
                    ontology.concept(lemma, create_if_necessary=True).add(full_lexical_form)

                except Exception:
                    print "Error parsing ontology. Unrecognized (lemma: ", lemma, ", tag: ", tag, ")"
                    continue

        return ontology

    @classmethod
    def from_resource(cls):
        _file = resources.get_config("resources", "freeling_dict")
        return FreelingDictionaryParser().parse_ontology(_file, "Freeling")


