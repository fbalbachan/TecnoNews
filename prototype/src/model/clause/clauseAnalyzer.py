#-*- coding: utf-8 -*-
from src.ling.verb_info import allowed_boxes, allowed_boxes_for_passive_verbs, allowed_boxes_for_unimember_sentences
from src.model.anaphora.gerundSubjectSolver import GerundSubjectSolver
from src.model.anaphora.personalPronounSolver import PersonalPronounSolver
from src.model.anaphora.relativeEntityExtractor import RelativeEntityExtractor
from src.model.anaphora.relativePronounSolver import RelativePronounSolver
from src.model.entity.entityExtractor import EntityExtractor
from src.model.entity.verb import Verb
from src.model.syntax.activeVoiceSyntacticAnalizer import ActiveVoiceSyntacticAnalyzer
from src.model.syntax.passiveVoiceSyntacticAnalyzer import PassiveVoiceSyntacticAnalyzer
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure
from src.model.syntax.valuatedAdverbFinder import ValuatedAdverbFinder


class ClauseAnalyzer:

    def __init__(self):
        self.context = {}

    def analyze(self, clause):
        clause.voice = self.voice_of(clause)
        if clause.voice: clause.verb = self.verb_of(clause)

        clause.entities = self.entities_of(clause)
        self.create_empty_syntactic_structures_for(clause)
        self.perform_prior_relative_analysis_of(clause)

        for method in self.analyze_order_for(clause): method(clause)

    def analyze_order_for(self, clause):
        relative_solver_order = [ self.analyze_syntactically, self.solve_relative ]
        if self.relative_needs_to_be_solved_first(clause):
            relative_solver_order.reverse()

        return relative_solver_order + [self.solve_gerund, self.solve_personal_pronouns, self.find_adverbs,
                                        self.find_unassigned_adjectives ]

    def relative_needs_to_be_solved_first(self, clause):
        if not clause.is_relative(): return False

        unique_destination_linkers = [ ["quien"], ["quienes"], ["cuyo"], ["cuya"], ["cuyos"], ["cuyas"], ["lo", "cual"]]
        is_equative_que = lambda clause: clause.relative_linker_words() == ["que"] and clause.voice and \
            clause.verb.transitivity == "EQUATIVE"
        if clause.relative_linker_words() in unique_destination_linkers or is_equative_que(clause): return True

    def perform_prior_relative_analysis_of(self, clause):
        if clause.is_relative():
            clause.relative_entity = RelativeEntityExtractor(clause).extract()
            if clause.relative_entity:
                clause.relative_linker = RelativePronounSolver.guess_linker_leaves(clause)

    def create_empty_syntactic_structures_for(self, clause):
        for name in self.allowed_syntactic_structures_for(clause):
            clause.syntactic_structures.append(SyntacticStructure(name, clause))

    def find_unassigned_adjectives(self, clause):
        all_assigned_leaves = sum([ entity.node.leaves() for entity in clause.entities if not entity.father ], [])
        print [ entity.proper_node.leaves() for entity in clause.entities ]
        clause.isolated_adjectives = filter(lambda leaf: not leaf in all_assigned_leaves,
                                            clause.proper_tree().leaves_of_category("adjective"))

    def find_adverbs(self, clause):
        clause.valuated_adverbs = ValuatedAdverbFinder(clause).find()

    def solve_relative(self, clause):
        if clause.is_relative() and clause.relative_entity: RelativePronounSolver(clause).solve()

    def solve_gerund(self, clause):
        if clause.voice and clause.is_gerund():
            GerundSubjectSolver(clause).solve()

    def solve_personal_pronouns(self, clause):
        PersonalPronounSolver(clause, self.context).solve()

    def analyze_syntactically(self, clause):
        syntactic_analyzer_by_voice = { "active" : ActiveVoiceSyntacticAnalyzer,
                                       "passive" : PassiveVoiceSyntacticAnalyzer,
                                       None : SyntacticAnalyzer }
        analyzer = syntactic_analyzer_by_voice[clause.voice](clause)
        analyzer.analyze(clause)

    def allowed_syntactic_structures_for(self, clause):
        active_voice_structures  = lambda clause: allowed_boxes(clause.verb.transitivity)
        passive_voice_structures = lambda clause: allowed_boxes_for_passive_verbs
        none_voice_structures = lambda clause: allowed_boxes_for_unimember_sentences
        structures_getter_by_voice = { \
                                 None :  none_voice_structures,
                                 "active" : active_voice_structures,
                                 "passive" : passive_voice_structures }
        return structures_getter_by_voice[clause.voice](clause)

    def verb_of(self, clause):
        node = self.verb_node_of(clause)
        leaves = self.verb_leaves_of(clause, node)
        return Verb(node, clause.voice, leaves)

    # Debido a que en voz passiva freeling no agrupa las hojas verbales
    def verb_leaves_of(self, clause, node):
        def leaves_of_passive_voice(clause, node):
            leaves = []
            root = clause.proper_tree()
            auxiliar_node = root.nodes_with_labels("vaux")
            if auxiliar_node: leaves.extend(auxiliar_node[0].leaves())

            ser_node = root.nodes_with_labels(["vser", "parti-ser"])
            if ser_node: leaves.extend(ser_node[0].leaves())

            leaves.extend(node.leaves())
            return leaves

        def leaves_of_active_voice(clause, node):
            root = clause.proper_tree()
            leaves = node.leaves_of_category("verb")

            if leaves[0].lemma == "estar": return [ leaves[0] ]

            ser_node = filter(lambda child: not child.is_leaf() and child.label == "parti-ser", root.children)
            if ser_node: leaves.extend(ser_node[0].leaves())
            return leaves

        verbal_leaves_by_voice = { "active" : leaves_of_active_voice, "passive" : leaves_of_passive_voice }

        return verbal_leaves_by_voice[clause.voice](clause, node)

    def verb_node_of(self, clause):
        root = clause.proper_tree()
        verb_nodes = root.nodes_with_labels([ "subord-ger", "verb", "parti-flex" ])
        verb_nodes = sorted(verb_nodes, key = lambda node: node.level())

        node = verb_nodes[0]
        if node.label == "subord-ger": node = node.leaves()[0]
        return node

    def entities_of(self, clause):
        return EntityExtractor(clause).extract()

    def voice_of(self, clause):
        root = clause.proper_tree()
        voice_by_label = { "subord-ger": "active", "grup-verb" : "active", "verb-pass" : "passive" }

        if root.label in voice_by_label: return voice_by_label[root.label]

        if root.subordinates_others():
            verbal_node = set([ child.label for child in root if not child.is_leaf() ]) & set(voice_by_label.keys())
            if len(verbal_node) > 1: raise Exception("Se encontró más de un verbo subordinado")
            return voice_by_label[verbal_node.pop()]

        return None
