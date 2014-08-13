# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import tacit_subjects
from src.ling.verb_info import get_sentimental_script_of, get_transitivity
from src.model.entity.entity import Entity


# Que el verbo sea una entidad es una licencia como también que exista una función sintáctica superior "verbo".
class Verb(Entity):

    def __init__(self, node, voice, leaves):
        Entity.__init__(self, node)

        self.voice = voice
        self._leaves = leaves

        lemma = self.lemma()
        self.msi = self.guess_msi()
        self.lexical_form = " ".join([ str(leaf) for leaf in self._leaves])

        self.sentimental_script = get_sentimental_script_of(lemma)
        self.transitivity = get_transitivity(lemma)

    def leaves(self):
        return self._leaves

    def lemma(self):
        return self.leaf().lemma

    def leaf(self):
        return self._leaves[-1]

    def modal_verb(self):
        if not self.is_compound(): return None
        leaves = self._leaves[-2:]
        if leaves[1].msi["mode"] == "infinitive": return leaves[0]

    def is_modal_of(self, lemma):
        modal = self.modal_verb()
        return modal and modal.lemma == lemma

    def is_compound(self):
        return len(self._leaves) > 1

    def guess_msi(self):
        first_leaf = self._leaves[0]

        person = first_leaf.msi["person"]
        gender = "neutral" if self.voice == "active" else (self.leaf().msi["gender"] or "neutral")
        number = first_leaf.msi["number"]
        mode = first_leaf.msi["mode"]

        return { "category" : "verb", "gender" : gender, "number" : number, "person" : person, "mode" : mode }

    def matching_pronoun(self):
        neutral_pronouns = { (1, "singular"), (2, "singular"), (2, "plural") }

        msi = self.msi
        person = msi["person"]
        number = msi["number"]
        gender = "neutral" if (person, number) in neutral_pronouns else msi["gender"]
        return tacit_subjects[(person, number, gender)]

    def matching_pronoun_msi(self):
        msi = self.msi
        return { "category" : "pronoun", "person" : msi["person"], "number" : msi["number"], "gender" : msi["gender"],
                "type" : "personal", "case" : None, "semantic_classification" : None }

    def __repr__(self):
        return " ".join([ str(leaf) for leaf in self._leaves]) + " (" + self.lemma() + ") " + \
            " ".join([ self.voice, self.sentimental_script.klass, self.transitivity ]) + " " + str(self.msi["person"]) + "°"
