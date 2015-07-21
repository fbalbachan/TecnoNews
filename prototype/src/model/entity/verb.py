# -*- coding: utf-8 -*-
from src.ling.genderEnum import GenderEnum
from src.ling.numberEnum import NumberEnum
from src.ling.tacit_subjects import tacit_subjects
from src.ling.verb_info import get_sentimental_script_of, get_transitivity, get_script_animity_for
from src.model.entity.entity import Entity

debug_mode = False


# The verb being an entity is a license, same as the existence of a superior syntactic function "Verb".
class Verb(Entity):

    def __init__(self, node, voice, leaves):
        if debug_mode: print "--> Verb.init(node: ", node, ")"
        Entity.__init__(self, node)

        self.voice = voice
        self._leaves = leaves

        lemma = self.lemma()
        self.msi = self.guess_msi()
        self.lexical_form = " ".join([str(leaf) for leaf in self._leaves])

        self.sentimental_script = get_sentimental_script_of(lemma)
        self.transitivity = get_transitivity(lemma)

        self.subject_animity = get_script_animity_for(lemma, "subject")
        self.affected_object_animity = get_script_animity_for(lemma, "od")  # "od"/"equative"/"regimen" are equivalent

    def leaves(self):
        return self._leaves

    def lemma(self):
        return self.leaf().lemma

    def leaf(self):
        return self._leaves[-1]

    def modal_verb(self):
        if self.is_compound():
            leaves = self._leaves[-2:]
            if leaves[1].msi["mode"] == "infinitive":
                return leaves[0]

        return None

    def has_modal(self):
        return self.modal_verb() is not None

    def is_modal_of(self, lemma):
        modal = self.modal_verb()
        return modal and modal.lemma == lemma

    def is_compound(self):
        return len(self._leaves) > 1

    def has_compound_time(self):
        return self.is_compound() and self.leaves()[0].lemma == "haber"

    def is_locution(self):
        return self.leaf().size() > 1

    def guess_msi(self):
        first_leaf = self._leaves[0]

        person = first_leaf.msi["person"]

        if self.voice == "active":
            gender = GenderEnum.neutral
        else:
            gender = (self.leaf().msi["gender"] or GenderEnum.neutral)

        number = first_leaf.msi["number"]
        mode = first_leaf.msi["mode"]
        time = first_leaf.msi["time"]

        return {"category": "verb", "gender": gender, "number": number,
                "person": person, "mode": mode, "time": time}

    def matching_pronoun(self):
        neutral_pronouns = {(1, NumberEnum.singular),
                            (2, NumberEnum.singular),
                            (2, NumberEnum.plural)}
        msi = self.msi
        person = msi["person"]
        number = msi["number"]
        gender = GenderEnum.neutral if (person, number) in neutral_pronouns else msi["gender"]
        return tacit_subjects[(person, number, gender)]

    def matching_pronoun_msi(self):
        msi = self.msi
        return {"category": "pronoun", "person": msi["person"], "number": msi["number"],
                 "gender": msi["gender"], "type": "personal", "case": None, "semantic_classification": None}

    def get_script_animity_for(self, structure_name):
        if structure_name == "subject":
            return self.subject_animity

        elif structure_name in ["od", "regimen", "equative"]:
            return self.affected_object_animity

        else:
            return None

    def __repr__(self):
        return " ".join([str(leaf) for leaf in self._leaves]) + " (" + self.lemma() + ") " + \
               " ".join([self.voice, self.sentimental_script.klass, self.transitivity]) + " " + \
               str(self.msi["person"]) + "°"

    slots_with_scripted_animity = ["subject", "od", "regimen", "equative"]