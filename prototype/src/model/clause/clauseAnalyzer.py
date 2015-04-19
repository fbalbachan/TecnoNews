#-*- coding: utf-8 -*-
from src.ling.verb_info import allowed_boxes, allowed_boxes_for_passive_verbs, allowed_boxes_for_unimember_sentences
from src.model.anaphora.gerundSubjectSolver import GerundSubjectSolver
from src.model.anaphora.personalPronounSolver import PersonalPronounSolver
from src.model.anaphora.relativeEntityExtractor import RelativeEntityExtractor
from src.model.anaphora.relativePronounSolver import RelativePronounSolver
from src.model.entity.entityExtractor import EntityExtractor
from src.model.entity.verbExtractor import VerbExtractor
from src.model.syntax.activeVoiceSyntacticAnalizer import ActiveVoiceSyntacticAnalyzer
from src.model.syntax.dateTimeFinder import DateTimeFinder
from src.model.syntax.passiveVoiceSyntacticAnalyzer import PassiveVoiceSyntacticAnalyzer
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure
from src.model.syntax.valuatedAdverbFinder import ValuatedAdverbFinder


class ClauseAnalyzer:

    def __init__(self):
        self.context = {}

    def analyze(self, clause):
		#print "Entering Clause.Analyze"
        clause.voice = self.voice_of(clause)
        if clause.voice:
            clause.verb = self.verb_of(clause)

        clause.entities = self.entities_of(clause)

        self.create_empty_syntactic_structures_for(clause)

        self.perform_prior_relative_analysis_of(clause)

        analyze_methods = self.analyze_order_for(clause)
        for method in analyze_methods:
            method(clause)

        self.analyze_kind_of_cataphoric_structure_of(clause)

    def analyze_kind_of_cataphoric_structure_of(self, clause):
        if clause.has_structure("subject") \
           and clause.structure("subject").is_tacit() \
           and clause.has_kind_of_cataphoric_structure():

            clause.attributes.append("pseudo_cataphoric")

    def analyze_order_for(self, clause):
        relative_solver_order = [ self.analyze_syntactically, self.solve_relative ]

        if ClauseAnalyzer.relative_needs_to_be_solved_first(clause):
            relative_solver_order.reverse()

        return relative_solver_order + [self.solve_gerund,
                                        self.solve_personal_pronouns,
                                        self.find_adverbs,
                                        self.find_unassigned_adjectives,
                                        self.find_time_references]

    @staticmethod
    def relative_needs_to_be_solved_first(clause):
        if not clause.is_relative():
            return False

        is_equative_que = lambda clause: clause.relative_linker_words() == ["que"] \
                                         and clause.voice \
                                         and clause.verb.transitivity == "EQUATIVE"

        unique_destination_linkers = [ ["quien"], ["quienes"], ["cuyo"], ["cuya"], ["cuyos"], ["cuyas"], ["lo", "cual"]]
        if clause.relative_linker_words() in unique_destination_linkers or is_equative_que(clause):
            return True

    def perform_prior_relative_analysis_of(self, clause):
        if clause.is_relative():
            clause.relative_entity = RelativeEntityExtractor(clause).extract()
            if clause.relative_entity:
                clause.relative_linker = RelativePronounSolver.guess_linker_leaves(clause)

    def create_empty_syntactic_structures_for(self, clause):
        for name in self.allowed_syntactic_structures_for(clause):
            structure = SyntacticStructure(name, clause)
            clause.syntactic_structures.append(structure)

    def find_unassigned_adjectives(self, clause):
        entities_and_verb = clause.entities + [ clause.verb ] if clause.voice else []
        all_assigned_leaves = sum([ entity.leaves() for entity in entities_and_verb if not entity.father ], [])

        adjectives_and_participles = clause.proper_tree().leaves_of_category("adjective") + \
            clause.proper_tree().leaves_of_msi({ "category" : "verb", "mode" : "participio" })

        clause.isolated_adjectives = filter(lambda leaf: not leaf in all_assigned_leaves, adjectives_and_participles)

    def find_adverbs(self, clause):
        clause.valuated_adverbs = ValuatedAdverbFinder(clause).find()

    def find_time_references(self, clause):
        clause.time_references = DateTimeFinder(clause).find()

    def solve_relative(self, clause):
        #print "Entering solve_relative"
        if clause.is_relative() and clause.relative_entity: RelativePronounSolver(clause).solve()

    def solve_gerund(self, clause):
        #print "Entering solve_gerund"
        if clause.voice and clause.is_gerund():
            GerundSubjectSolver(clause).solve()

    def solve_personal_pronouns(self, clause):
        #print "Entering solve_personal_pronouns"
        PersonalPronounSolver(clause, self.context).solve()

    def analyze_syntactically(self, clause):
        #print "Entering analyze_syntactically"
        syntactic_analyzer_by_voice = {"active" : ActiveVoiceSyntacticAnalyzer,
                                       "passive" : PassiveVoiceSyntacticAnalyzer,
                                       None : SyntacticAnalyzer}
        analyzer = syntactic_analyzer_by_voice[clause.voice](clause)
        analyzer.analyze(clause)

    def allowed_syntactic_structures_for(self, clause):
        active_voice_structures  = lambda clause: allowed_boxes(clause.verb.transitivity)
        passive_voice_structures = lambda clause: allowed_boxes_for_passive_verbs
        none_voice_structures = lambda clause: allowed_boxes_for_unimember_sentences
        structures_getter_by_voice = { None :  none_voice_structures,
                                       "active" : active_voice_structures,
                                       "passive" : passive_voice_structures }
        return structures_getter_by_voice[clause.voice](clause)

    def verb_of(self, clause):
        return VerbExtractor(clause).extract()

    def entities_of(self, clause):
        #print "Entering entities_of"
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
