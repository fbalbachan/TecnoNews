# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


# TODO: Cambiar a SiAEncasodequeStrategy agregando el cambio de encabezado
class SiAEncasodequeStrategySubjunctivePart:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        if clause.voice == "active" \
           and not verb.has_compound_time() \
           and verb.matches_msi({"mode": "indicative"}) \
           and not verb.is_locution():
            # Defensive programming here:
            # TODO: To use only the condition above, first check all tenses
            return self.original_text(verb) != self.subjunctive_text(verb)
        return False

    def rewrite(self, clause):
        verb = clause.verb

        rewritten_verb = self.subjunctive_text(verb)

        return Rewrite(verb.node, set_first_letter_case(verb.leaves()[0].original_lexical_form, rewritten_verb))

    def original_text(self, verb):
        # TODO: Check this
        return " ".join([leaf.original_lexical_form for leaf in verb.node.leaves()])

    def subjunctive_text(self, verb):
        ontology = self.ontology
        try:
            inflected_leaf = verb.modal_verb() if verb.has_modal() else verb.leaf()
            if inflected_leaf.msi['time'] == 'pasado':
                # subjunctive de haber
                haber_lf = ontology.get_lexical_form("haber", self.haber_subjunctive_msi_for(inflected_leaf))
                participle_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.participle_msi)

                rewritten_verb = haber_lf.text + " " + participle_lf.text

            else:
                subjunctive_lf = ontology.get_lexical_form(inflected_leaf.lemma,
                                                           SiAEncasodequeStrategySubjunctivePart.msi_for(inflected_leaf))
                rewritten_verb = subjunctive_lf.text

            if verb.has_modal():
                rewritten_verb += " " + verb.leaf().lexical_form

        except:
            rewritten_verb = self.original_text(verb)

        return rewritten_verb

    @staticmethod
    def msi_for(verb):
        return {'number':  verb.number(),
                'person': 3 if verb.person() == 1 and verb.number() == 'singular' else verb.person(),
                'time':  verb.msi['time'],
                'mode': 'subjunctive'}

    def haber_subjunctive_msi_for(self, verb):
        return {"mode": "subjunctive",
                "time": "presente",
                "person": 3 if verb.person() == 1 and verb.number() == 'singular' else verb.person(),
                "number": verb.number()}

    participle_msi = {"mode": "participio",
                      "gender": Gender.masculine,
                      "number": Number.singular}
    type = "replacement"
