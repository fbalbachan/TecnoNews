# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


# TODO: Cambiar a SiAEncasodequeStrategy agregando el cambio de encabezado
class SiAEncasodequeStrategySubjunctivePart:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        if clause.voice == "active" and not verb.has_compound_time() \
                and verb.matches_msi({ "mode" : "indicative" }) and not verb.is_locution():
            # Defensive programming here:
            # TODO: To use only the condition above, first check all tenses
            return self.original_text(verb) != self.subjunctive_text(verb)
        return False

    def rewrite(self, clause):
        verb = clause.verb

        rewrited_verb = self.subjunctive_text(verb)

        return Rewrite(verb.node, set_first_letter_case(verb.leaves()[0].original_lexical_form, rewrited_verb))

    def original_text(self, verb):
        return str(verb.leaf()) # TODO: Check this

    def subjunctive_text(self, verb):
        ontology = self.ontology
        inflected_leaf = verb.modal_verb() if verb.has_modal() else verb.leaf()
        try:
            if inflected_leaf.msi['time'] == 'pasado':
                subjunctive_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.msi_for(inflected_leaf))

                # subjuntivo de haber
                haber_lf = ontology.get_lexical_form("haber", self.haber_subjunctive_msi_for(inflected_leaf))
                participle_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.participle_msi)

                rewrited_verb = haber_lf.text + " " + participle_lf.text

            else:
                subjunctive_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.msi_for(inflected_leaf))
                rewrited_verb = subjunctive_lf.text
        except:
            rewrited_verb = inflected_leaf.text

        if verb.has_modal(): rewrited_verb += " " + verb.leaf().lexical_form
        return rewrited_verb

    def msi_for(self, verb):
        msi = verb.msi
        return { 
            'number':  msi['number'],
            'person': 3 if msi['person'] == 1 and msi['number'] == 'singular' else msi['person'],
            'time':  msi['time'],
            'mode': 'subjuntive'
        }

    def haber_subjunctive_msi_for(self, verb):
        msi = verb.msi
        return {
            "mode" : "subjuntive",
            "time" : "presente",
            "person" : 3 if msi['person'] == 1 and msi['number'] == 'singular' else msi['person'],
            "number" : msi["number"]
        }

    participle_msi = { "mode" : "participio", "gender" : "masculine", "number" : "singular" }
    type = "replacement"
