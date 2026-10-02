# -*- coding: utf-8 -*-
from src.rewrite.strategy.textualCite import TextualCite
from src.utils.fact_compare import FactCompare

class TextSummarizer:
    def __init__(self, analysis):
        self.analysis = analysis
        self.verbs_que = TextualCite().verbs_que
        self.fact_compare = FactCompare()

    def summarize(self, extended=False):
        sentences = self.analysis["paragraph"].sentences

        final_text = ""
        extended_summary = []

        for a_sentence in sentences:
            if self._sentence_has_cite(a_sentence):
                continue

            main_clauses = a_sentence.main_clauses()

            for main_clause in main_clauses:
                if not main_clause.is_fact():
                    continue
                #STRUCTURES;
                subject_structure = None
                equative_structure = None
                #CONDITIONS:
                valid_subject = False
                valid_equative = False

                #GET RELEVANT STRUCTURES FROM MAIN CLAUSE:
                for a_structure in main_clause.syntactic_structures:
                    if a_structure.name == "subject":
                        subject_structure = a_structure
                    if a_structure.name == "equative":
                        equative_structure = a_structure

                #GENERAL AND SUBJECT VALIDATIONS:
                if main_clause.voice in ["active", "passive"] \
                    and not any(an_entity.is_impersonal() for an_entity in main_clause.all_entities()) \
                    and subject_structure is not None \
                    and len(subject_structure.all_entities()) > 0:

                        #GET DEREFERENCED ENTITY (IN SUBJECT)
                        dereferenced_entity = subject_structure.all_entities()[0]
                        if subject_structure.all_entities()[0].is_tacit():
                            dereferenced_entity = subject_structure.all_entities()[0].referenced_entity()

                        if dereferenced_entity is not None \
                            and not dereferenced_entity.is_tacit() \
                            and dereferenced_entity.kernel is not None \
                            and dereferenced_entity.kernel.msi["category"] == "noun":
                                valid_subject = True


                #EQUATIVE VALIDATIONS:
                if equative_structure is not None:
                    if len(equative_structure.all_entities()) > 0:

                        #GET DEREFERENCED ENTITY (IN EQUATIVE)
                        dereference_entity = equative_structure.all_entities()[0]
                        if equative_structure.all_entities()[0].is_tacit():
                            dereferenced_entity = equative_structure.all_entities()[0].referenced_entity()

                        if dereferenced_entity is not None\
                            and not dereferenced_entity.is_tacit()\
                            and dereferenced_entity.kernel is not None\
                            and dereferenced_entity.kernel.msi["category"] == "noun":
                                valid_equative = True
                else:
                    valid_equative = True

                if valid_subject and valid_equative:
                    if not extended:
                        final_text += "\n" + self._summarize_clause(main_clause)
                    else:
                        clause_data = self.fact_compare.extract_comparable_data(main_clause)
                        clause_data["text"] = self._summarize_clause(main_clause)
                        extended_summary.append(clause_data)

        if not extended:
            return final_text
        else:
            return extended_summary

    def _summarize_clause(self, a_clause):
        clause_text = a_clause.__repr__().replace("_", " ")

        #REMOVE TIME REFERENCES:
        time_lexical_forms = [" ".join([repr(l) for l in reference.leaves()]).replace("_", " ") for reference in a_clause.time_references]
        for a_time in time_lexical_forms:
            clause_text = clause_text.replace(a_time, "")

        #CLEAN:
        clause_text = clause_text.strip()
        if clause_text[-1] == ",":
            clause_text = clause_text[:-1]
        if clause_text[0] == ",":
            clause_text = clause_text[1:]
        clause_text = clause_text.strip()

        return clause_text


    def _sentence_has_cite(self, a_sentence):
        for a_clause in a_sentence.clauses:
            if a_clause.verb is not None and a_clause.verb.lemma() in self.verbs_que:

                struct_od = None
                for a_structure in a_clause.syntactic_structures:
                    if a_structure.name == "od":
                        struct_od = a_structure
                        break

                if struct_od is not None \
                    and len(struct_od.all_entities()) > 0 \
                    and struct_od.all_entities()[0].__repr__() == "(implicit) algo":
                        return True

        return False
