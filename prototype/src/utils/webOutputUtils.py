# -*- coding: utf-8 -*-
from src.utils.factNormalizer import FactNormalizer

class WebOutputUtils:

    def structure(self, clause, name):
        if clause.has_structure(name):
            structure = clause.structure(name)
            if name == "verb":
                return structure.entity().lemma()
            else:
                return ", ".join([ str(entity) for entity in structure.all_entities() ])
        else:
            return ""

    def valuated_adverbs(self, clause):
        return ", ".join([ str(adverb) for adverb in clause.valuated_adverbs ])

    def tooltip(self, clause, name):
        if clause.has_structure(name):
            return ", ".join([ self.entity_tooltip(entity) for entity in clause.structure(name).all_entities() ])
        else:
            return ""

    def entity_tooltip(self, entity):
        tooltip = self.msi_string(entity.msi)
        if entity.category() == "verb":
            tooltip = tooltip + " - Transitivity " + entity.transitivity + " - Sentiment script " + \
                entity.sentimental_script.klass
        return tooltip

    def e_sv_neg_ev(self, entity):
        return self.evidence_string(entity, 1, entity.sentimental_value.negative_evidence())

    def e_sv_pos_ev(self, entity):
        return self.evidence_string(entity, 0, entity.sentimental_value.positive_evidence())

    def evidence_string(self, entity, component, evidence_list):
        return ", ".join([ str(evidence.object) + " (" + str(evidence.value[component]) + ")" for evidence in
                          evidence_list])

    def msi_string(self, msi):
        return str(msi["person"]) + "° " + str(msi["gender"]) + " " + str(msi["number"]) + " (" + str(msi["category"]) + ")"
        #return ", ".join([ key + " = " + str(value) for (key, value) in msi.items() ])

    def global_operator_bullet_for(self, clause, klass):
        return "✓" if clause.has_global_operator_of(klass) else "☐"

    def clause_number(self, clause, sentence):
        number_string = ""
        while not clause.is_root():
            father = clause.father
            number = father.children.index(clause) + 1
            number_string = "." + str(number) + number_string
            clause = father

        number = sentence.clauses.index(clause) + 1
        number_string = str(number) + number_string

        return number_string

    def fact(self, clause):
        return FactNormalizer(clause).fact()

    def fact_real_or_not(self, clause):
        return "(Not a real fact. See checked flags in global operators.)" if clause.global_operators else ""

    def score_of(self, analysis, clause):
        summary = analysis["summary"][clause]
        return "%.2f,-%.2f" % (summary["positive"], summary["negative"])