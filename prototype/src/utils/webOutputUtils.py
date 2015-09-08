# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.utils.factNormalizer import FactNormalizer
from src.ling.tacit_subjects import tacit_subjects
from src.utils.configProvider import ConfigProvider
from _csv import reader
from src.ling.freelingDictionaryParser import FreelingDictionaryParser

debug_mode = False


class WebOutputUtils:

    def __init__(self):
        if debug_mode: print "--> WebOutputUtils.init()"
        self.synonyms = self._get_synonyms()
        self.ontology = FreelingDictionaryParser.from_resource()

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
            return ", ".join([self.entity_tooltip(entity) for entity in clause.structure(name).all_entities()])
        else:
            return ""

    def entity_tooltip(self, entity):
        tooltip = self.msi_string(entity.msi)
        tooltip = tooltip if not isinstance(tooltip, unicode) else tooltip.encode("utf-8")

        if (entity.category() == "noun" or entity.category() == "pronoun") \
           and "animity" in entity.msi:
            tooltip = tooltip + " " + entity.msi["animity"].encode("utf-8")

        if entity.is_named_entity():
            classification = str(entity.classification(look_deep=True)).upper()
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
        if debug_mode: print "--> WebOutputUtils.fact(clause:", clause, ")"
        return FactNormalizer(clause, self.ontology, self.synonyms).fact()

    def fact_real_or_not(self, clause):
        return "(Not a real fact. See checked flags in global operators.)" if not clause.is_fact() else ""

    def preferred_genders_numbers_to_unify_with(self, entities):
        preferred = {}
        for entity in entities:
            (gender, number) = (entity.gender(), entity.number())
            if gender == Gender.neutral or number == Number.invariable:
                (gender, number) = self.choose_gender_number(entity, entities)

            preferred[entity] = (gender, number)

        return preferred

    def preferred_classifications_to_unify_with(self, entities):
        preferred_classifications = {}
        for entity in entities:
            classification = entity.classification(look_deep=True)
            preferred_classifications[entity] = classification
            if classification is None:
                preferred_classifications[entity] = self.choose_classification(entity.real_name(), entities)
        return preferred_classifications

    def choose_classification(self, real_name, entities):
        same_name_entities = filter(lambda p_entity: p_entity.real_name() == real_name, entities)
        if same_name_entities and any(p_entity.is_named_entity() for p_entity in same_name_entities):
            entity = filter(lambda p_entity: p_entity.classification(look_deep=True) is not None, entities)[0]
            return entity.classification(look_deep=True)
        else:
            return None

    def choose_gender_number(self, entity, entities):
        same_pgn_entities = filter(lambda e:
                                      e.category() == entity.category()
                                      and e.msi["type"] == entity.msi["type"]
                                      and e.person() == entity.person()
                                      and (entity.gender() == Gender.neutral and e.gender() != Gender.neutral
                                           or entity.number() == Number.invariable and e.number() != Number.invariable)
                                      and e.matches_gender_of(entity)
                                      and e.matches_number_of(entity),
                                   entities)
        gender = Gender.neutral
        number = Number.invariable
        if same_pgn_entities:
            with_gender = filter(lambda e: e.gender() != Gender.neutral, same_pgn_entities)
            with_number = filter(lambda e: e.number() != Number.invariable, same_pgn_entities)
            gender = with_gender[0].gender()
            number = with_number[0].number()

        return gender, number

    def get_referents_data(self, entities):
        if debug_mode: print "--> WebOutputUtils.get_referents_data(entities:", entities, ")"
        preferred_genders_numbers = self.preferred_genders_numbers_to_unify_with(entities)
        preferred_classifications = self.preferred_classifications_to_unify_with(entities)

        [by_name_classification, singles] = \
            self.unify_by_name_classification(entities, preferred_classifications, preferred_genders_numbers)

        [third_person_pronouns, singles] = \
            self.unify_third_person_pronouns(singles, preferred_genders_numbers)

        [person_1_2_pronouns, singles] = \
            self.unify_pronouns(singles, preferred_genders_numbers)

        [plain_entities, singles] = \
            self.unify_plain_entities(singles)

        referents_data = by_name_classification \
                         + third_person_pronouns \
                         + person_1_2_pronouns \
                         + plain_entities \
                         + singles

        compare = lambda x, y: \
                           1 if len(x["refs"]) < len(y["refs"]) else -1 if len(x["refs"]) > len(y["refs"])\
                      else 1 if x["neg"] < y["neg"] else -1 if x["neg"] > y["neg"]\
                      else 1 if x["pos"] < y["pos"] else -1 if x["pos"] > y["pos"]\
                      else 1 if x["rn"] > y["rn"]   else -1 if x["rn"] < y["rn"]\
                      else 0

        referents_data = sorted(referents_data, cmp=compare)

        for referent_data in referents_data:
            referent_data["rn"] = referent_data["rn"] if referent_data["sc"] != "NONE" else referent_data["rn"].lower()

        return referents_data

    def unify_by_name_classification(self, entities, preferred_classifications, preferred_genders_numbers):
        if debug_mode: print "--> WebOutputUtils.unify_by_name_classification(entities:", entities, ")"

        entities_to_unify = [entity for entity in entities if entity.classification(look_deep=True) is not None
                                                              or preferred_classifications[entity] is not None]
        remainder_referents = []
        for entity in [entity for entity in entities if entity not in entities_to_unify]:
            real_name = entity.real_name()
            referent_data = {"re":   entity,  "refs": [entity],
                             "rn":   real_name.encode("utf-8") if isinstance(real_name, unicode) else real_name,
                             "pos":  entity.sentimental_value.value[0],
                             "neg":  entity.sentimental_value.value[1],
                             "sc":   "NONE"}
            remainder_referents += [referent_data]

        referents_dict = {}
        for entity in entities_to_unify:
            real_name = entity.real_name()
            classification = entity.classification(look_deep=True)
            classification = classification if classification else preferred_classifications[entity]

            nc_key = (real_name, classification)
            if nc_key not in referents_dict.keys():
                positive = entity.sentimental_value.value[0]
                negative = entity.sentimental_value.value[1]
                references = [entity]
            else:
                positive = referents_dict[nc_key]["pos"] + entity.sentimental_value.value[0]
                negative = referents_dict[nc_key]["neg"] + entity.sentimental_value.value[1]
                references = referents_dict[nc_key]["refs"] + [entity]

            real_name = real_name if classification else real_name.lower()
            referenced_entity = entity.referenced_entity()

            referent_data = {"re":   referenced_entity,
                             "refs": references,
                             "rn":   real_name.encode("utf-8") if isinstance(real_name, unicode) else real_name,
                             "pos":  positive,
                             "neg":  negative,
                             "sc":   str(classification).upper()}

            referents_dict[nc_key] = referent_data

        referents = referents_dict.values() + remainder_referents
        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents)
        return [unified, singles]

    def unify_pronouns(self, referents_data, preferred_genders_numbers):
        if debug_mode: print "--> WebOutputUtils.unify_pronouns(referents_data:", referents_data, ")"
        referents_to_unify = [ref for ref in referents_data
                                      if (ref["re"].category(), ref["re"].msi["type"]) == ("pronoun", "personal")]
        referents_to_unify = [ref for ref in referents_to_unify
                                      if ref["re"].person() in [1, 2]]
        referents_to_unify = [ref for ref in referents_to_unify
                                      if ref["re"].number() in [Number.singular, Number.plural]]

        pronouns_in_singular = [ref for ref in referents_to_unify if ref["re"].number() == Number.singular]
        [unified_singulars, singles1] = self.unify_singular_pronouns(pronouns_in_singular)

        pronouns_in_plural = [ref for ref in referents_to_unify if ref["re"].number() == Number.plural]
        [unified_plurals, singles2] = self.unify_plural_pronouns(pronouns_in_plural, preferred_genders_numbers)

        other_referents = [ref for ref in referents_data if ref not in referents_to_unify]

        referents = unified_singulars + unified_plurals + singles1 + singles2 + other_referents
        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents)
        return [unified, singles]

    def unify_third_person_pronouns(self, referents_data, preferred_genders_numbers):
        if debug_mode: print "--> WebOutputUtils.unify_third_person_pronouns(referents_data:", referents_data, ")"
        pronouns_in_third = \
            [ref for ref in referents_data
             if (ref["re"].category(), ref["re"].msi["type"], ref["re"].person()) == ("pronoun", "personal", 3)]

        other_referents = [ref for ref in referents_data if ref not in pronouns_in_third]

        dict_by_gender_number = {}
        for pronoun_data in pronouns_in_third:
            pronoun = pronoun_data["re"]
            gender = Gender.most_specific(pronoun.gender(), preferred_genders_numbers[pronoun][0])
            number = Number.most_specific(pronoun.number(), preferred_genders_numbers[pronoun][1])
            name = str(pronoun.referenced()).lower() if pronoun.is_linked() else pronoun.real_name()

            key = (gender, number)
            if key in dict_by_gender_number.keys():
                positive = dict_by_gender_number[key]["pos"] + pronoun.sentimental_value.value[0]
                negative = dict_by_gender_number[key]["neg"] + pronoun.sentimental_value.value[1]
                references = dict_by_gender_number[key]["refs"] + [pronoun]
            else:
                positive = pronoun.sentimental_value.value[0]
                negative = pronoun.sentimental_value.value[1]
                references = [pronoun]

            new_referent_data = {"re":   pronoun,
                                 "refs": references,
                                 "rn":   name,
                                 "pos":  positive,
                                 "neg":  negative,
                                 "sc":   "NONE"}

            dict_by_gender_number[key] = new_referent_data

        referents = dict_by_gender_number.values() + other_referents
        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents)
        return [unified, singles]

    def unify_singular_pronouns(self, pronouns_in_singular):
        if debug_mode: print "--> WebOutputUtils.unify_singular_pronouns(prons_in_singular:", pronouns_in_singular, ")"
        sing_pronouns_dict = {}
        for referent_data in pronouns_in_singular:
            entity = referent_data["re"]
            name = "yo" if entity.person() == 1 else "tú"

            person = entity.person()
            if person in sing_pronouns_dict.keys():
                references = sing_pronouns_dict[person]["refs"] + [entity]
                positive = sing_pronouns_dict[person]["pos"] + referent_data["pos"]
                negative = sing_pronouns_dict[person]["neg"] + referent_data["neg"]
            else:
                positive = referent_data["pos"]
                negative = referent_data["neg"]
                references = [entity]

            new_referent_data = {"re":   entity,
                                 "refs": references,
                                 "rn":   name,
                                 "pos":  positive,
                                 "neg":  negative,
                                 "sc":   "NONE"}

            sing_pronouns_dict[person] = new_referent_data

        referents = sing_pronouns_dict.values()
        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents)
        return [unified, singles]

    def unify_plural_pronouns(self, pronouns_in_plural, preferred_genders_numbers):
        if debug_mode: print "--> WebOutputUtils.unify_plural_pronouns(prons_in_plural:", pronouns_in_plural, ")"
        dict_by_person_gender = {}
        for referent_data in pronouns_in_plural:
            entity = referent_data["re"]
            gender = Gender.most_specific(entity.gender(), preferred_genders_numbers[entity][0])
            number = Number.most_specific(entity.number(), preferred_genders_numbers[entity][1])
            name = tacit_subjects[entity.person(), number, gender]
            pgn_key = (entity.person(), gender)

            if pgn_key in dict_by_person_gender.keys():
                positive = dict_by_person_gender[pgn_key]["pos"] + referent_data["pos"]
                negative = dict_by_person_gender[pgn_key]["neg"] + referent_data["neg"]
                references = dict_by_person_gender[pgn_key]["refs"] + [entity]
            else:
                positive = referent_data["pos"]
                negative = referent_data["neg"]
                references = [entity]

            name = name if referent_data["sc"] else name.lower()

            new_referent_data = {"re":   entity,
                                 "refs": references,
                                 "rn":   name,
                                 "pos":  positive,
                                 "neg":  negative,
                                 "sc":   str(referent_data["sc"]).upper()}

            dict_by_person_gender[pgn_key] = new_referent_data

        referents = dict_by_person_gender.values()
        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents)
        return [unified, singles]

    def unify_plain_entities(self, plain_referents_data):
        if debug_mode: print "--> WebOutputUtils.unify_plain_entities(plain_referents_data:", plain_referents_data, ")"
        atomic_plain_referents_data = [ref for ref in plain_referents_data if not ref["re"].children]
        non_atomic_plain_referents_data = [ref for ref in plain_referents_data if ref["re"].children]

        [unified_atomic, singles1] = \
            self.unify_plain_referents(atomic_plain_referents_data, is_atomic=True)

        [unified_non_atomic, singles2] = \
            self.unify_plain_referents(non_atomic_plain_referents_data, is_atomic=False)

        referents_data = unified_atomic + unified_non_atomic + singles1 + singles2

        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, referents_data)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, referents_data)
        return [unified, singles]

    def unify_plain_referents(self, plain_refs_data, is_atomic):
        if debug_mode: print "--> WebOutputUtils.unify_plain_entities(plain_refs_data:", plain_refs_data, ")"
        unified_referents = []
        while len(plain_refs_data) > 0:
            unified = plain_refs_data.pop(0)
            for plain_referent in plain_refs_data[:]:
                if self.plain_entities_match(plain_referent["re"], unified["re"]):
                    unified["rn"] = self.get_real_name_for_plain_entities(plain_referent["re"], unified["re"], is_atomic)
                    unified["pos"] = unified["pos"] + plain_referent["pos"]
                    unified["neg"] = unified["neg"] + plain_referent["neg"]
                    unified["refs"] = unified["refs"] + [plain_referent["re"]]
                    if plain_referent in plain_refs_data:
                        plain_refs_data.remove(plain_referent)

            unified_referents.append(unified)

        unified = filter(lambda ref_data: len(ref_data["refs"]) > 1, unified_referents)
        singles = filter(lambda ref_data: len(ref_data["refs"]) == 1, unified_referents)
        return [unified, singles]

    def get_real_name_for_plain_entities(self, entity1, entity2, is_atomic):
        if debug_mode: print "--> WebOutputUtils.get_real_name_for_plain_entities(entity1:", entity1, ", entity2:", entity2, ", is_atomic:", str(is_atomic),")"

        if self.kernels_are_synonyms(entity1, entity2):
            object1 = entity1.kernel if is_atomic else entity1
            object2 = entity2.kernel if is_atomic else entity2
            real_name = object1.lexical_form if entity1.kernel.lemma <= self.synonyms[entity1.kernel.lemma] \
                        else object2.lexical_form

        else:
            object = entity1.kernel if (hasattr(entity1, "kernel") and is_atomic) else entity1
            real_name = object.lexical_form

        real_name = real_name.encode("utf-8") if isinstance(real_name, unicode) else real_name

        if debug_mode: print "<-- get_real_name_for_plain_entities:", real_name
        return real_name

    def plain_entities_match(self, entity1, entity2):
        if debug_mode: print "--> WebOutputUtils.plain_entities_match(entity1:", entity1, ", entity2:", entity2, ")"

        both_have_kernel =     hasattr(entity1, "kernel") and entity1.kernel \
                           and hasattr(entity2, "kernel") and entity2.kernel

        if both_have_kernel and self.are_synonyms(entity1.kernel, entity2.kernel):
            return True

        msi_match = True
        if both_have_kernel:
            for key, value in entity1.kernel.msi.iteritems():
                key_value_match = key in entity2.kernel.msi.keys() and entity2.kernel.msi[key] == value \
                                  or key not in entity2.kernel.msi.keys()
                msi_match = msi_match and key_value_match
            kernels_match = self.kernels_match(entity1.kernel, entity2.kernel)
            match = msi_match and kernels_match

        else:
            for key, value in entity1.msi.iteritems():
                msi_match = msi_match and ((key in entity2.msi.keys() and entity2.msi[key] == value)
                                           or (key not in entity2.msi.keys()))
            same_lexical_form = entity1.lexical_form.lower() == entity2.lexical_form.lower()
            match = msi_match and same_lexical_form

        if debug_mode: print "<-- plain_entities_match:", str(match)
        return match

    def kernels_match(self, kernel1, kernel2):
        if debug_mode: print "--> WebOutputUtils.kernels_match(kernel1:", kernel1, ", kernel2:", kernel2, ")"
        match = kernel1.lexical_form.lower() == kernel2.lexical_form.lower() \
                or self.are_synonyms(kernel1, kernel2)

        if debug_mode: print "<-- kernels_match:", str(match)
        return match

    def kernels_are_synonyms(self, entity1, entity2):
        if debug_mode: print "--> WebOutputUtils.kernels_are_synonyms(entity1:", entity1, ", entity2:", entity2, ")"

        both_have_kernel =     hasattr(entity1, "kernel") and entity1.kernel is not None \
                           and hasattr(entity2, "kernel") and entity2.kernel is not None

        are_synonyms = self.are_synonyms(entity1.kernel, entity2.kernel) if both_have_kernel \
                       else False

        if debug_mode: print "<-- kernels_are_synonyms:", str(are_synonyms)
        return are_synonyms

    def are_synonyms(self, kernel1, kernel2):
        if debug_mode: print "--> WebOutputUtils.are_synonyms(lemma1:", kernel1.lemma, ", lemma2:", kernel2.lemma, ")"
        lemma1 = kernel1.lemma
        lemma2 = kernel2.lemma
        are_synonyms = lemma1 in self.synonyms.keys() and self.synonyms[lemma1] == lemma2

        if debug_mode: print "<-- are_synonyms:", str(are_synonyms)
        return are_synonyms

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