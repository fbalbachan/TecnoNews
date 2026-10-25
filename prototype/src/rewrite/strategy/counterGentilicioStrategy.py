# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'


from src.utils.csvwrapper import unicode_csv_reader
from src.utils.configProvider import ConfigProvider
from src.rewrite.rewrite import Rewrite
from unidecode import unidecode
import re


class CounterGentilicioStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.forbidden_words = ["todo", "toda", "nada", "parte", "medio",
                                "hispano", "hispana", "británico", "británica",
                                "jerónimo", "jerónima", "norteamericano", "norteamericana"]


    def applies_to(self, a_clause):
        return (self.get_country_match(a_clause) is not None)

    def get_country_match(self, a_clause):
        clause_entities = a_clause.assigned_entities()
        for an_entity in clause_entities:
            if an_entity.kernel is None or an_entity.kernel.lexical_form in self.forbidden_words:
                continue
            entity_nodes = an_entity.node.leaves()

            gent_node = None
            #SEARCH FOR RELEVANT NODES
            for a_node in entity_nodes:
                if a_node.lemma in self.forbidden_words:
                    continue

                if a_node.lemma.lower() in gent_list:
                    if 'category' in a_node.msi and a_node.msi['category'] == 'adjective':
                        gent_node = a_node
                        break


            gent_prefix_len = 5
            country_found = False
            country_match = None
            if gent_node is not None:
                while gent_prefix_len >= 3 and not country_found:
                    regex=re.compile("^"+gent_node.lexical_form[:gent_prefix_len].lower()+".*")
                    country_match = [a_country for a_country in countries_list for a_match in [regex.search(a_country.lower().replace("_", " "))] if a_match]
                    if len(country_match) > 0:
                        country_match = country_match[0]
                        country_found = True
                    else:
                        gent_prefix_len -= 1

                #NOT FOUND => SEARCH FOR CITIES
                if not country_found:
                    gent_prefix_len = 5
                    while gent_prefix_len >= 3 and not country_found:
                        regex=re.compile("^"+gent_node.lexical_form[:gent_prefix_len].lower()+".*")
                        country_match = [a_country for a_country in countries_cities_list for a_match in [regex.search(a_country.lower().replace("_", " "))] if a_match]
                        if len(country_match) > 0:
                            country_match = country_match[0]
                            country_found = True
                        else:
                            gent_prefix_len -= 1

                if country_found:
                    return {'gentilicio': gent_node.lexical_form, 'entity': an_entity, 'country': country_match, 'gent_node': gent_node}
        return None

    def rewrite(self, clause):
        return self.rewrite_clause(clause)

    def rewrite_clause(self, a_clause):
        gent_match = self.get_country_match(a_clause)

        if gent_match is not None:
            an_entity = gent_match['entity']
            a_gent = gent_match['gentilicio']
            a_country = gent_match['country']
            return Rewrite(gent_match["gent_node"].father, "de " + a_country)

        return []

    type = "replacement"


config = ConfigProvider()
countries_cities_file = config.get("resources", "countries_cities")
countries_cities_reader = unicode_csv_reader(open(countries_cities_file, 'r', encoding="utf-8"), first_line_is_header=False, delimiter=',')
countries_cities_list = [country[0] for country in countries_cities_reader]

countries_file = config.get("resources", "countries")
countries_reader = unicode_csv_reader(open(countries_file, 'r', encoding="utf-8"), first_line_is_header=False, delimiter=',')
countries_list = [country[0] for country in countries_reader]

gent_file = config.get("resources", "demonyms")
gent_reader = unicode_csv_reader(open(gent_file, 'r', encoding="utf-8"), first_line_is_header=False, delimiter=',')
gent_list = [gent[0] for gent in gent_reader]
