# -*- coding: utf-8 -*-
from src.utils.factNormalizer import FactNormalizer


class WebOutputUtils:

    def structure(self, clause, name):
        if clause.has_structure(name) and not clause.structure(name).is_empty():
            structure = clause.structure(name)
            if name == "verb":
                return structure.entity().lemma()
            else:
                entities = structure.all_entities()
                infinity = 10000
                entities.sort(key=lambda p_entity: p_entity.token.start() if p_entity.is_explicit() else infinity)
                return ", ".join([str(entity) for entity in entities])
        else:
            return ""

    def valuated_adverbs(self, clause):
        return ", ".join([ str(adverb) for adverb in clause.valuated_adverbs ])

    def time_references(self, clause):
        time_lexical_forms = [ " ".join([repr(l) for l in reference.leaves()]) for reference in clause.time_references ]
        return ", ".join(time_lexical_forms)

    def tooltip(self, clause, name):
        if clause.has_structure(name):
            return ", ".join([ self.entity_tooltip(entity) for entity in clause.structure(name).all_entities() ])
        else:
            return ""

    def entity_tooltip(self, entity):
        tooltip = self.msi_string(entity.msi)
        tooltip = tooltip if not isinstance(tooltip, unicode) \
                  else tooltip.encode("utf-8")

        if (entity.category() == "noun" or entity.category() == "pronoun") \
           and "animity" in entity.msi:
            animity = entity.msi["animity"]
            animity = animity if not isinstance(animity, unicode) \
                      else animity.encode("utf-8")
            tooltip = tooltip + " " + animity

        if entity.category() == "noun" and entity.msi["type"] == "proper":
            semantic_classification = str(entity.msi["semantic_classification"]).upper()
            semantic_classification = semantic_classification if not isinstance(semantic_classification, unicode) \
                                      else semantic_classification.encode("utf-8")
            tooltip = tooltip + " " + semantic_classification

        if entity.category() == "verb":
            transitivity = entity.transitivity if not isinstance(entity.transitivity, unicode) \
                           else entity.transitivity.encode("utf-8")
            klass = entity.sentimental_script.klass if not isinstance(entity.sentimental_script.klass, unicode) \
                    else entity.sentimental_script.klass.encode("utf-8")

            tooltip = tooltip + " - Transitivity " + transitivity + " - Sentiment script " + klass

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
        return "(Not a real fact. See checked flags in global operators.)" if not clause.is_fact() else ""

    def semantic_classification(self, entity):
        proper_entity = entity.referent.designated_ref() if ("referent" in dir(entity) and entity.referent is not None) \
                        else entity

        if proper_entity.category() == "noun" and proper_entity.msi["type"] == "proper":
            return proper_entity.msi["semantic_classification"].upper()

        return "NONE"

    def get_referents_data(self, entities):
        referents_dict = dict()

        for entity in entities:
            if entity.is_linked():
                name = entity.referenced().lexical_form
                referent_entity = entity.referenced()

                if "referent" in dir(referent_entity) and referent_entity.referent is not None:
                    name = referent_entity.referent.name()
                    referent_entity = referent_entity.referent.designated_ref()

            elif "referent" in dir(entity) and entity.referent is not None:
                name = entity.referent.name()
                referent_entity = entity.referent.designated_ref()

            else:
                referent_entity = entity
                name = referent_entity.lexical_form

            semantic_classification = self.semantic_classification(referent_entity)
            if semantic_classification is None or semantic_classification == "NONE":
                name = name.lower()

            positive = entity.sentimental_value.value[0]/100.0
            negative = entity.sentimental_value.value[1]/100.0

            key = (name, semantic_classification)
            count = 1
            if key in referents_dict.keys():
                positive += referents_dict[key][2]
                negative += referents_dict[key][3]
                count += referents_dict[key][5]

            referents_dict[key] = (referent_entity,
                                   name,
                                   positive, negative,
                                   semantic_classification,
                                   count)

        compare = lambda x, y: \
                           1 if (x[3] < y[3] and y[3] - x[3] > 0.001)\
                     else -1 if (x[3] > y[3] and x[3] - y[3] > 0.001)\
                     else  1 if (x[2] < y[2] and y[2] - x[2] > 0.001)\
                     else -1 if (x[2] > y[2] and x[2] - y[2] > 0.001)\
                     else  0

        referents_data = sorted(referents_dict.values(), cmp=compare)
        return referents_data

    def score_of(self, analysis, object):
        try:
            summary = analysis["summary"][object]
            return "%.2f,-%.2f" % (summary["positive"], summary["negative"])
        except Exception:
            return "--,--"

    def tree_icon(self, referent):
        return "static/icon/%s.png" % referent.semantic_classification().lower()

    def e_tag_list(self, referent, name, tag_mapping):
        existing_references = [ reference for reference in referent.references_with(name) if reference in tag_mapping ]
        return ",".join([ tag_mapping[reference] for reference in existing_references ])







