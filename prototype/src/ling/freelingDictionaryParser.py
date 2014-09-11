# -*- coding: utf-8 -*-
from src.ling.msi_mapper import tag2fullmsi
from src.ontology.lexicalForm import LexicalForm
from src.ontology.ontology import Ontology
from src.utils.resources import instance as resources


class FreelingDictionaryParser:
    def parse_ontology(self, _file, ontology_name):
        ontology = Ontology(ontology_name)
        for line in open(_file):
            tokens = line.strip().split()

            lexical_form = tokens[0]

            lemmas = tokens[1::2]
            tags = tokens[2::2]

            for lemma, tag in zip(lemmas, tags):
                if "+" in lemma: continue
                ontology.concept(lemma, True).add(LexicalForm(lexical_form, tag2fullmsi(tag), lemma, None))

        return ontology

    @classmethod
    def from_resource(cls):
        _file = resources.get_config("resources", "freeling_dict")
        return FreelingDictionaryParser().parse_ontology(_file, "Freeling")
