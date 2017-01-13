# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'


from src.utils.csvwrapper import unicode_csv_reader
from src.utils.configProvider import ConfigProvider
from src.rewrite.rewrite import Rewrite
import re


class GentilicioStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        #self.forbidden_words = ["por", "hasta", "entre", "desde"]

    '''
    def applies_to(self, sentence, node):
        return any((self.applies_to_clause(clause) for clause in sentence.clauses))
    '''

    def applies_to(self, a_clause):
        return (self.get_gent_match(a_clause) is not None)

    def get_gent_match(self, a_clause):
        clause_entities = a_clause.assigned_entities()
        for an_entity in clause_entities:
            if an_entity.kernel is None:
                continue
            entity_nodes = an_entity.node.leaves()

            #SEARCH FOR RELEVANT NODES
            previous_de = None
            country_node = None
            for a_node in entity_nodes:
                if a_node.father.label == 'w-ms' and previous_de is not None:
                    country_node = a_node
                    break

                previous_de = None
                if a_node.father.label == 'sp-de':
                    previous_de = a_node



            if previous_de is not None and country_node is not None:
                for a_country in countries_list:
                    if a_country in an_entity.lexical_form.decode("utf-8"):
                        country_prefix_len = 5
                        gent_found = False
                        gent_match = None
                        while country_prefix_len >= 3 and not gent_found:
                            regex=re.compile("^"+a_country[:country_prefix_len].lower()+".*")
                            gent_match = [a_match.group(0) for a_gent in gent_list for a_match in [regex.search(a_gent)] if a_match]
                            if len(gent_match) > 0:
                                gent_match = gent_match[0]
                                gent_found = True
                            else:
                                country_prefix_len -= 1

                        if gent_found:
                            return {'gentilicio': gent_match, 'entity': an_entity, 'country': a_country, 'de_node': previous_de, 'country_node': country_node}
        return None

    def rewrite(self, clause):
        return self.rewrite_clause(clause)

    def rewrite_clause(self, a_clause):
        gent_match = self.get_gent_match(a_clause)
        an_entity = gent_match['entity']
        a_gent = gent_match['gentilicio']
        a_country = gent_match['country']

        rewrites = []
        if gent_match is not None:
            gent_info = self.ontology.get_lemma_and_msi(a_gent.encode("utf-8"))
            concepts = self.ontology.concept(gent_info["lemma"])

            target_msi = an_entity.kernel.msi
            for a_concept in concepts.lexical_forms:
                if a_concept.msi["category"] == "adjective":
                        if "number" in a_concept.msi and "number" in target_msi and a_concept.msi["number"] == target_msi["number"]:
                            if "gender" in a_concept.msi and "gender" in target_msi and a_concept.msi["gender"] == target_msi["gender"]:
                                return Rewrite(gent_match["de_node"].father, a_concept.text)
                                #return repr(a_clause).replace("_", " ").replace("de " + a_country.encode("utf-8"), a_concept.text)

        return []

    type = "replacement"


config = ConfigProvider()
countries_file = config.get("resources", "countries")
countries_reader = unicode_csv_reader(open(countries_file, 'r'), first_line_is_header=False, delimiter=',')
countries_list = [unicode(country[0], 'utf-8') for country in countries_reader]

gent_file = config.get("resources", "demonyms")
gent_reader = unicode_csv_reader(open(gent_file, 'r'), first_line_is_header=False, delimiter=',')
gent_list = [unicode(gent[0], 'utf-8') for gent in gent_reader]
