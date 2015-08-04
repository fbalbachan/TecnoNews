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
        tooltip = tooltip if not isinstance(tooltip, unicode) else tooltip.encode("utf-8")

        if (entity.category() == "noun" or entity.category() == "pronoun") \
           and "animity" in entity.msi:
            tooltip = tooltip + " " + entity.msi["animity"].encode("utf-8")

        if entity.is_named_entity():
            classification = str(entity.classification(False)).upper()
            tooltip = tooltip + " " + classification.encode("utf-8")

        if entity.category() == "verb":
            transitivity = entity.transitivity.encode("utf-8")
            klass = entity.sentimental_script.klass.encode("utf-8")
            tooltip = tooltip + " - Transitivity " + transitivity + " - Sentiment script " + klass

        return tooltip

    def e_sv_pos_ev(self, entities):
        return ", ".join([self.evidence_string(entity, 0, entity.sentimental_value.positive_evidence())
                          for entity in entities if entity.sentimental_value.value[0] > 0])

    def e_sv_neg_ev(self, entities):
        return ", ".join([self.evidence_string(entity, 1, entity.sentimental_value.negative_evidence())
                          for entity in entities if entity.sentimental_value.value[1] > 0])

    def evidence_string(self, entity, component, evidence_list):
        return ", ".join([str(evidence.object) + " (" + str(evidence.value[component]) + ")"
                          for evidence in evidence_list])

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

    def choose_classifications_to_unify_with(self, entities):
        chosen_classifications = {}
        for entity in entities:
            real_name = entity.real_name()
            if entity.classification(False) is None:
                chosen_classifications[entity] = self.choose_classification(real_name, entities)
        return chosen_classifications

    def choose_classification(self, real_name, entities):
        same_name_entities = filter(lambda p_entity: p_entity.real_name() == real_name, entities)
        if same_name_entities and any(p_entity.is_named_entity() for p_entity in same_name_entities):
            first_named_entity = filter(lambda p_entity: p_entity.is_named_entity(), entities)[0]
            return first_named_entity.classification(False)
        else:
            return None

    def get_referents_data(self, entities):
        chosen_classifications = self.choose_classifications_to_unify_with(entities)
        referents_dict = {}
        for entity in entities:
            referenced_entity = entity.referenced_entity()
            references = [entity]
            real_name = entity.real_name()
            positive = entity.sentimental_value.value[0]
            negative = entity.sentimental_value.value[1]
            classification = entity.classification(False)
            count = 1

            key = (real_name, classification if classification else chosen_classifications[entity])
            if key in referents_dict.keys():
                positive += referents_dict[key]["pos"]
                negative += referents_dict[key]["neg"]
                count += referents_dict[key]["cnt"]
                references = referents_dict[key]["refs"] + references

            real_name = real_name if key[1] else real_name.lower()

            referent_data = {"re":   referenced_entity,
                             "refs": references,
                             "rn":   real_name,
                             "pos":  positive,
                             "neg":  negative,
                             "sc":   str(key[1]).upper(),
                             "cnt":  count}

            referents_dict[key] = referent_data


        compare = lambda x, y: \
                          1 if x["cnt"] < y["cnt"] else -1 if x["cnt"] > y["cnt"]\
                     else 1 if x["neg"] < y["neg"] else -1 if x["neg"] > y["neg"]\
                     else 1 if x["pos"] < y["pos"] else -1 if x["pos"] > y["pos"]\
                     else 1 if x["rn"] < y["rn"]   else -1 if x["rn"] > y["rn"]\
                     else 0

        referents_data = sorted(referents_dict.values(), cmp=compare)
        return referents_data

    def score_of(self, analysis, object):
        try:
            summary = analysis["summary"][object]
            return "%.2f,-%.2f" % (summary["positive"], summary["negative"])
        except Exception:
            return "--,--"

    def tree_icon(self, referent):
        return "static/icon/%s.png" % str(referent.semantic_classification()).lower()

    def e_tag_list(self, referent, name, tag_mapping):
        existing_references = [reference for reference in referent.references_with(name) if reference in tag_mapping]
        return ",".join([tag_mapping[reference] for reference in existing_references])
