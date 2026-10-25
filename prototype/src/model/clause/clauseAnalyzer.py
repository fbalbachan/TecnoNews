# -*- coding: utf-8 -*-
from src.ling.verb_info import allowed_boxes, allowed_boxes_for_passive_verbs, allowed_boxes_for_minor_sentences
from src.model.anaphora.gerundSubjectSolver import GerundSubjectSolver
from src.model.anaphora.personalPronounSolver import PersonalPronounSolver
from src.model.anaphora.relativeEntityExtractor import RelativeEntityExtractor
from src.model.anaphora.relativePronounSolver import RelativePronounSolver
from src.model.entity.entityExtractor import EntityExtractor
from src.model.entity.verbExtractor import VerbExtractor
from src.model.entity.entity import Entity
from src.model.syntax.activeVoiceSyntacticAnalizer import ActiveVoiceSyntacticAnalyzer
from src.model.syntax.dateTimeFinder import DateTimeFinder
from src.model.syntax.passiveVoiceSyntacticAnalyzer import PassiveVoiceSyntacticAnalyzer
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure
from src.model.syntax.valuatedAdverbFinder import ValuatedAdverbFinder
from src.model.syntax.appositionFinder import AppositionFinder

debug_mode = False


class ClauseAnalyzer:

    def __init__(self, global_context={}):
        if debug_mode: print("--> ClauseAnalyzer.init()")

        self.context = {}
        self.global_context = global_context

    def analyze(self, clause):
        if debug_mode: print("-->  Clause.Analyze (clause: ", clause, ")")

        clause.voice = ClauseAnalyzer.voice_of(clause)
        if clause.voice:
            clause.verb = ClauseAnalyzer.verb_of(clause)

        clause.entities = ClauseAnalyzer.entities_of(clause, self.global_context)

        ClauseAnalyzer.find_time_references(clause)

        self.link_appositions(clause)

        ClauseAnalyzer.create_empty_syntactic_structures_for(clause)

        ClauseAnalyzer.perform_prior_relative_analysis_of(clause)

        analyze_methods = self.get_analyzer_solver_and_finder_methods_in_order(clause)
        for method in analyze_methods:
            method(clause)

        ClauseAnalyzer.analyze_kind_of_cataphoric_structure_of(clause)

    def get_analyzer_solver_and_finder_methods_in_order(self, clause):
        if debug_mode: print("-->  ClauseAnalyzer.get_analyzer_solver_and_finder_methods_in_order()")

        if ClauseAnalyzer.relative_needs_to_be_solved_first(clause):
            methods = [ClauseAnalyzer.solve_relative, ClauseAnalyzer.analyze_syntactically]
        else:
            methods = [ClauseAnalyzer.analyze_syntactically, ClauseAnalyzer.solve_relative]

        methods += [ClauseAnalyzer.solve_gerund,
                    self.solve_personal_pronouns,
                    ClauseAnalyzer.find_adverbs,
                    ClauseAnalyzer.find_unassigned_adjectives]

        return methods

    @staticmethod
    def relative_needs_to_be_solved_first(clause):
        if debug_mode: print("-->  ClauseAnalyzer.relative_needs_to_be_solved_first()")

        if not clause.is_relative():
            return False

        is_equative_que = lambda clause_var: clause_var.relative_linker_words() == ["que"] \
                                             and clause_var.voice \
                                             and clause_var.verb.transitivity == "EQUATIVE"

        unique_destination_linkers = [["quien"], ["quienes"],
                                      ["cuyo"], ["cuya"], ["cuyos"], ["cuyas"],
                                      ["lo", "cual"]]

        return clause.relative_linker_words() in unique_destination_linkers \
               or is_equative_que(clause)

    @staticmethod
    def analyze_kind_of_cataphoric_structure_of(clause):
        if clause.has_structure("subject") \
                and clause.structure("subject").is_tacit() \
                and clause.has_kind_of_cataphoric_structure():

            clause.attributes.append("pseudo_cataphoric")

    @staticmethod
    def perform_prior_relative_analysis_of(clause):
        if clause.is_relative():
            clause.relative_entity = RelativeEntityExtractor(clause).extract()
            if clause.relative_entity:
                clause.relative_linker = RelativePronounSolver.guess_linker_leaves(clause)

    @staticmethod
    def create_empty_syntactic_structures_for(clause):
        for name in ClauseAnalyzer.allowed_syntactic_structures_for(clause):
            structure = SyntacticStructure(name, clause)
            clause.syntactic_structures.append(structure)

    @staticmethod
    def find_unassigned_adjectives(clause):
        entities_and_verb = clause.entities + [clause.verb] if clause.voice else []
        all_assigned_leaves = sum([entity.leaves() for entity in entities_and_verb if not entity.father], [])

        adjectives_and_participles = clause.proper_tree().leaves_of_category("adjective") \
                                    + clause.proper_tree().leaves_of_msi({"category": "verb", "mode": "participio"})

        clause.isolated_adjectives = [leaf for leaf in adjectives_and_participles if leaf not in all_assigned_leaves]

    @staticmethod
    def link_appositions(clause):
        if debug_mode: print("-->  ClauseAnalyzer.link_appositions(clause)")
        if not clause.voice:
            return

        finder = AppositionFinder(clause)
        appositions = finder.retrieve_appositions()
        for (head, rest) in appositions:
            if debug_mode: print("Linking Apposition: ", head, " --> ", rest)
            Entity.link_in_apposition(head, rest)
            for entity in rest:
                for nested_entity in entity.get_nested_entities(True):
                    clause.entities.remove(nested_entity)

    @staticmethod
    def find_adverbs(clause):
        clause.valuated_adverbs = ValuatedAdverbFinder(clause).find()

    @staticmethod
    def find_time_references(clause):
        # Time references are parsing-tree-nodes (structures) with expressions about time.
        clause.time_references = DateTimeFinder(clause).find()

        # Entities created from nodes referencing time most probably are not proper entities.
        # So we add them to clause.time_entities, and remove them from clause.entities to avoid its use in SVO slots
        clause.put_apart_time_entities()

    @staticmethod
    def solve_relative(clause):
        if debug_mode: print("-->  solve_relative ( relative entity: ", clause.relative_entity, ")")

        if clause.is_relative() and clause.relative_entity:
            RelativePronounSolver(clause).solve()

    @staticmethod
    def solve_gerund(clause):
        if debug_mode: print("-->  solve_gerund (voice, ", clause.voice, " - is gerund: ", str(clause.is_gerund()), ")")

        if clause.voice and clause.is_gerund():
            GerundSubjectSolver(clause).solve()

    def solve_personal_pronouns(self, clause):
        if debug_mode: print("-->  solve_personal_pronouns")

        PersonalPronounSolver(clause, self.context).solve()

    @staticmethod
    def analyze_syntactically(clause):
        if debug_mode: print("-->  analyze_syntactically")

        syntactic_analyzer_by_voice = {"active":  ActiveVoiceSyntacticAnalyzer,
                                       "passive": PassiveVoiceSyntacticAnalyzer,
                                       None:      SyntacticAnalyzer}

        analyzer = syntactic_analyzer_by_voice[clause.voice](clause)

        analyzer.analyze(clause)

    @staticmethod
    def allowed_syntactic_structures_for(clause):
        if debug_mode: print("-->  ClauseAnalyzer.allowed_syntactic_structures_for(clause: ", clause, ")")
        active_voice_structures = lambda clause_var: allowed_boxes(clause_var.verb.transitivity)
        passive_voice_structures = lambda clause_var: allowed_boxes_for_passive_verbs
        none_voice_structures = lambda clause_var: allowed_boxes_for_minor_sentences

        structures_getter_by_voice = {None:      none_voice_structures,
                                      "active":  active_voice_structures,
                                      "passive": passive_voice_structures}

        return structures_getter_by_voice[clause.voice](clause)

    @staticmethod
    def verb_of(clause):
        if debug_mode: print("--> ClauseAnalyzer.verb_of(clause: ", clause, ")")
        verb = VerbExtractor(clause).extract()
        return verb

    @staticmethod
    def entities_of(clause, global_context={}):
        if debug_mode: print("--> ClauseAnalyzer.entities_of")
        return EntityExtractor(clause, global_context=global_context).extract()

    @staticmethod
    def voice_of(clause):
        root = clause.proper_tree()
        voice_by_label = {"subord-ger": "active", "grup-verb": "active", "verb-pass": "passive"}

        if root.label in voice_by_label:
            return voice_by_label[root.label]

        if root.subordinates_others():
            verbal_node = set([child.label for child in root if not child.is_leaf()]) \
                          & set(voice_by_label.keys())

            if len(verbal_node) > 1:
                raise Exception("Se encontró más de un verbo subordinado")

            return voice_by_label[verbal_node.pop()]

        return None
