# -*- coding: utf-8 -*-
from src.ling.genderEnum import GenderEnum
from src.ling.numberEnum import NumberEnum
from src.utils.factNormalizer import FactNormalizer
from src.ling.tacit_subjects import tacit_subjects

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

    def preferred_gender_number_to_unify_with(self, entities):
        preferred_genders_numbers = {}
        for entity in entities:
            (gender, number) = (entity.msi["gender"], entity.msi["number"])
            if gender == GenderEnum.neutral or number == NumberEnum.invariable:
                (gender, number) = self.choose_gender_number(real_name, entities)

            preferred_genders_numbers[entity] = (gender, number)

        return preferred_genders_numbers

    def preferred_classifications_to_unify_with(self, entities):
        preferred_classifications = {}
        for entity in entities:
            if entity.classification(False) is None:
                preferred_classifications[entity] = self.choose_classification(entity.real_name(), entities)
        return preferred_classifications

    def choose_classification(self, real_name, entities):
        same_name_entities = filter(lambda p_entity: p_entity.real_name() == real_name, entities)
        if same_name_entities and any(p_entity.is_named_entity() for p_entity in same_name_entities):
            first_named_entity = filter(lambda p_entity: p_entity.is_named_entity(), entities)[0]
            return first_named_entity.classification(False)
        else:
            return None

    def get_referents_data(self, entities):

        referents_data = self.unify_by_name_classification(entities)

        unified_referents_data = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents_data)
        single_referents_data = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents_data)

        referents_data = self.unify_pronouns(entities, single_referents_data)

        unified_referents_data += filter(lambda ref_data: len(ref_data["refs"]) > 1, referents_data)
        single_referents_data = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents_data)

        referents_data = self.unify_plain_entities(single_referents_data)

        for entity in entities:
            referenced_entity = entity.referenced_entity()
            references = [entity]
            real_name = entity.real_name()
            positive = entity.sentimental_value.value[0]
            negative = entity.sentimental_value.value[1]
            classification = entity.classification(False)
            classification = classification if classification else preferred_classifications[entity]
            count = 1


            if nc_key in referents_dict.keys():
                positive += referents_dict[nc_key]["pos"]
                negative += referents_dict[nc_key]["neg"]
                count = referents_dict[nc_key]["cnt"] + 1
                references = referents_dict[nc_key]["refs"] + references

            elif gn_key in pronouns_dict.keys() \
                 and entity.msi["category"] == "pronoun" \
                 and entity.msi["type"] == "personal" \
                 and entity.msi["person"] in [1, 2]:

                real_name = tacit_subjects[(gn_key[0], gender, number)]
                positive += referents_dict[nc_key]["pos"]
                negative += referents_dict[nc_key]["neg"]
                count = referents_dict[nc_key]["cnt"] + 1
                references = referents_dict[nc_key]["refs"] + references

            real_name = real_name if classification else real_name.lower()

            referent_data = {"re":   referenced_entity,
                             "refs": references,
                             "rn":   real_name,
                             "pos":  positive,
                             "neg":  negative,
                             "sc":   str(classification).upper(),
                             "cnt":  count}

            referents_dict[nc_key] = pronouns_dict[gn_key] = referent_data

        compare = lambda x, y: \
                          1 if x["cnt"] < y["cnt"] else -1 if x["cnt"] > y["cnt"]\
                     else 1 if x["neg"] < y["neg"] else -1 if x["neg"] > y["neg"]\
                     else 1 if x["pos"] < y["pos"] else -1 if x["pos"] > y["pos"]\
                     else 1 if x["rn"] > y["rn"]   else -1 if x["rn"] < y["rn"]\
                     else 0

        referents_data = list(set(referents_dict.values() + pronouns_dict.values()))

        referents_data = sorted(referents_data, cmp=compare)
        return referents_data

    def unify_by_name_classification(self, entities):

        preferred_classifications = self.preferred_classifications_to_unify_with(entities)
        referents_dict = {}

        for entity in entities:
            real_name = entity.real_name()
            classification = entity.classification(False)
            classification = classification if classification else preferred_classifications[entity]

            nc_key = (real_name, classification)
            if nc_key not in referents_dict.keys():
                positive = entity.sentimental_value.value[0]
                negative = entity.sentimental_value.value[1]
                references = [entity]
                count = 1
            else:
                positive = referents_dict[nc_key]["pos"] + entity.sentimental_value.value[0]
                negative = referents_dict[nc_key]["neg"] + entity.sentimental_value.value[1]
                references = referents_dict[nc_key]["refs"] + [entity]
                count = referents_dict[nc_key]["cnt"] + 1

            real_name = real_name if classification else real_name.lower()
            referenced_entity = entity.referenced_entity()

            referent_data = {"re":   referenced_entity,
                             "refs": references,
                             "rn":   real_name,
                             "pos":  positive,
                             "neg":  negative,
                             "sc":   str(classification).upper(),
                             "cnt":  count}

            referents_dict[nc_key] = referent_data

        return referents_dict.values()

    def unify_pronouns(self, entities, referents_data):
        preferred_genders_numbers = self.preferred_genders_numbers_to_unify_with(entities)
        pronouns_dict = {}
        for referent_data in referents_data:
            entity = referent_data["refs"][0]
            preferred_gn = preferred_genders_numbers[entity]
            gender = entity.msi["gender"] if entity.msi["gender"] is not GenderEnum.neutral else preferred_gn[0]
            number = entity.msi["number"] if entity.msi["number"] is not NumberEnum.invariable else preferred_gn[1]

            pgn_key = (entity.msi["person"], gender, number)
            if pgn_key in pronouns_dict.keys() \
                 and entity.msi["category"] == "pronoun" \
                 and entity.msi["type"] == "personal" \
                 and entity.msi["person"] in [1, 2]:

                real_name = tacit_subjects[pgn_key]
                positive = pronouns_dict[pgn_key]["pos"] + referent_data["pos"]
                negative = pronouns_dict[pgn_key]["neg"] + referent_data["neg"]
                references = pronouns_dict[pgn_key]["refs"] + referent_data["refs"]
                count = pronouns_dict[pgn_key]["cnt"] + 1

            else:
                positive = referent_data["pos"]
                negative = referent_data["neg"]
                references = referent_data["refs"]
                count = referent_data["cnt"]

            real_name = real_name if classification else real_name.lower()
            referenced_entity = entity.referenced_entity()

            referent_data = {"re":   referenced_entity,
                             "refs": references,
                             "rn":   real_name,
                             "pos":  positive,
                             "neg":  negative,
                             "sc":   str(classification).upper(),
                             "cnt":  count}

            referents_dict[nc_key] = referent_data

        return referents_dict.values()





















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
