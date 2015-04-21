# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import tacit_subjects
from src.ling.verb_info import get_sentimental_script_of, get_transitivity, get_script_animity_for
from src.model.entity.entity import Entity
from src.model.entity.animity_enum import AnimityEnum


# Que el verbo sea una entidad es una licencia como también que exista una función sintáctica superior "verbo".
class Verb(Entity):

    def __init__(self, node, voice, leaves):
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
        if not self.is_compound():
            return None
        leaves = self._leaves[-2:]
        if leaves[1].msi["mode"] == "infinitive":
            return leaves[0]

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
        gender = "neutral" if self.voice == "active" else (self.leaf().msi["gender"] or "neutral")
        number = first_leaf.msi["number"]
        mode = first_leaf.msi["mode"]
        time = first_leaf.msi["time"]

        return {"category": "verb", "gender": gender, "number": number,
                "person": person, "mode": mode, "time": time}

    def matching_pronoun(self):
        neutral_pronouns = {(1, "singular"), (2, "singular"), (2, "plural")}

        msi = self.msi
        person = msi["person"]
        number = msi["number"]
        gender = "neutral" if (person, number) in neutral_pronouns else msi["gender"]
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

    def get_valid_matching_animity(self, structure_name, entity):
        if structure_name in self.boxes_with_scripted_animity:
            script_animity = self.get_script_animity_for(structure_name)
            if entity.animity_matches(script_animity):
                return AnimityEnum.most_specific(script_animity, entity.msi["animity"])

        return None

    def __repr__(self):
        return " ".join([str(leaf) for leaf in self._leaves]) + " (" + self.lemma() + ") " + \
               " ".join([self.voice, self.sentimental_script.klass, self.transitivity]) + " " + \
               str(self.msi["person"]) + "°"

    boxes_with_scripted_animity = ["subject", "od", "regimen", "equative"]