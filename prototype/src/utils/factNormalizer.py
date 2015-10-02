# -*- coding: utf-8 -*-

from src.utils.configProvider import ConfigProvider
from src.ling.synonyms import Synonyms
from _csv import reader
from src.ling.gender import Gender
#from src.parser.labelNode import LabelNode

debug_mode = False


class FactNormalizer:
    def __init__(self, clause, ontology):
        if debug_mode: print "--> FactNormalizer.init(node: ", clause, ")"
        self.clause = clause
        self.synonyms = Synonyms()
        self.ontology = ontology

    def fact(self):
        fact = ""
        clause = self.clause
        # structure_order = ["subject", "verb", "od", "oi", "regimen", "equative", "instrument_goal", "adjuncts"]
        structure_order = ["subject", "verb", "od", "regimen", "equative"]

        for structure_name in structure_order:

            if clause.has_structure(structure_name):

                if fact:
                    fact += " + "
                structure = clause.structure(structure_name)

                if structure.is_empty():
                    fact += "∅"

                else:

                    if structure_name == "verb":
                        replacement = self._get_verb_replacement(clause)

                    else:
                        lexical_forms = []
                        for entity in structure.all_entities():

                            if entity.is_linked():
                                entity = entity.referenced()

                            replacement = entity.lexical_form

                            if not (entity.is_tacit() or entity.is_impersonal()):
                                lemmas = [leaf.lemma for leaf in entity.leaves()]
                                if lemmas == ["quién"]:
                                    replacement = "alguien"

                                elif lemmas == ["qué"] and entity.category() == "pronoun" \
                                                       and entity.msi["type"] == "interrogative":
                                    replacement = "algo"
                                #
                                # elif type(entity.node) is LabelNode and entity.node.label == "grup-verb-inf":
                                #    replacement = entity.node.leaves()[0].lexical_form
                                #
                                elif hasattr(entity, "kernel") and entity.kernel:
                                    lemma = entity.kernel.lemma
                                    print entity.kernel.msi
                                    if entity.kernel.msi["category"] == "noun" \
                                       and entity.kernel.msi["type"] == "articulo":
                                        replacement = entity.lexical_form

                                    elif not self.synonyms.get_base_synonym(lemma):
                                        replacement = entity.kernel.lexical_form

                                    else:
                                        base_synonym = self.synonyms.get_base_synonym(lemma)
                                        if '_' in base_synonym or base_synonym not in self.ontology.concepts:
                                            # if synonym in self.locutions and self.locutions[synonym]:
                                            #    pass
                                            replacement = base_synonym.replace('_', ' ')
                                        else:
                                            concept = self.ontology.concept(base_synonym)
                                            leaf_msi = self._msi_transform(entity.kernel.msi)

                                            forms = [form for form in concept.lexical_forms if leaf_msi == self._msi_transform(form.msi)]
                                            if not forms:
                                                try:
                                                    del leaf_msi["gender"]
                                                except KeyError:
                                                    pass

                                                for form in concept.lexical_forms:
                                                    transformed_msi = self._msi_transform(form.msi)
                                                    try:
                                                        del transformed_msi["gender"]
                                                    except KeyError:
                                                        pass

                                                    print "modified Leaf MSI:", leaf_msi
                                                    if transformed_msi == leaf_msi:
                                                        print "entering"
                                                        replacement = form.text
                                                        break
                                            else:
                                                replacement = forms[0].text

                            lexical_forms.append(replacement)

                        replacement = ", ".join(lexical_forms)

                    fact += replacement

        time_lexical_forms = [" ".join([repr(l) for l in reference.leaves()]) for reference in clause.time_references]
        fact = fact + " --TIME: " + ", ".join(time_lexical_forms)
        return fact

    @staticmethod
    def fact_real_or_not(clause):
        return "(Not a real fact. See checked flags in global operators.)" if not clause.is_fact() else ""

    def _get_verb_replacement(self, clause):
        lemma = clause.verb.lemma()
        verb_replacement = lemma
        if self.synonyms.get_base_synonym(lemma):
            synonym = self.synonyms.get_base_synonym(lemma)
            verb_replacement = synonym

        return verb_replacement

    def string_of(self, entity):
        if entity.is_linked():
            entity = entity.referenced()

        if entity.category() == "verb":
            return entity.lemma()

        if entity.is_tacit() or entity.is_impersonal():
            return entity.lexical_form

        lemmas = [leaf.lemma for leaf in entity.leaves()]
        if lemmas == ["quién"]:
            return "alguien"

        if lemmas == ["qué"] and entity.category() == "pronoun" \
                             and entity.msi["type"] == "interrogative":
            return "algo"

        return str(entity)

    def _get_synonyms(self):
        return self._get_replacements_from_csv("synonyms")

    def _get_replacements_from_csv(self, resource):
        # Warning, it is a dict, it doesn't work for multiple replacements for the same word.

        replacements = {}
        config = ConfigProvider()
        replacements_filename = config.get("resources", resource)
        for line in reader(open(replacements_filename, 'r')):
            replacements[line[0]] = line[1]
            replacements[line[1]] = line[0]
        return replacements

    def _msi_transform(self, msi):
        if debug_mode: print "--> SynonymsStrategy._msi_transform(msi: ", msi, ")"

        result_msi = {}
        if 'number' in msi:
            result_msi['number'] = msi['number']
        if 'gender' in msi:
            result_msi['gender'] = msi['gender']

        if msi['category'] == 'adjective':
            if 'grade' in msi:
                result_msi['grade'] = msi['grade']
        elif msi['category'] == 'verb':
            if 'mode' in msi:
                result_msi['mode'] = msi['mode']
            if 'person' in msi:
                result_msi['person'] = msi['person']
            if 'time' in msi:
                result_msi['time'] = msi['time']
        result_msi['category'] = msi['category']
        return result_msi
