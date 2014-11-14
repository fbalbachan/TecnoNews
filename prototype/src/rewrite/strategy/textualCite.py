# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.parser.leafNode import LeafNode
from src.parser.labelNode import LabelNode
import ConfigParser

#TODO: add case when the root is f-no-c and all the cases
#CLAUSE_SEPARATORS

class TextualCite:
    def __init__(self, dislocation=None, changes=None):
        if dislocation is None:
            self.dislocation = [True, False]

        # TODO: fixme why we use this value on changes?
        # which value should we use?
        # if changes is None:
        #     self.changes = ["de_acuerdo_con", ""]

        self.verbs_que = self._get_verbs_que()

    def applies_to(self, sentence, node):
        return self.applies_segun_inicial(sentence, node)

    def applies_segun_inicial(self, sentence, node):

        cite_indexes = self.find_children_cite_indexes(node)

        applies = isinstance(node, LabelNode) and node.label == 'grup-verb' \
            and (
                len(node.children) >= 3 and

                isinstance(node.children[0], LabelNode) and
                node.children[0].label == 'sn' and

                isinstance(node.children[1], LabelNode) and
                node.children[1].label == 'verb' and

                node.children[1].children[0].lemma in self.verbs_que and

                isinstance(node.children[2], LabelNode) and
                (node.children[2].label == 'Fc' or
                 (node.children[2].label == 'F-no-c' and
                  node.children[2].children[0].lemma == ':')) and

                isinstance(node.children[cite_indexes[0]], LabelNode) and
                node.children[cite_indexes[0]].label == 'F-no-c' and

                isinstance(node.children[cite_indexes[1]], LabelNode) and
                node.children[cite_indexes[1]].label == 'F-no-c'
            )

        return applies

    def _get_verbs_que(self):
        verbs_que = []
        config = ConfigParser.ConfigParser()
        config.read("config")
        verbs_que_filename = config.get("resources", "verbs_que")

        for line in open(verbs_que_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                verbs_que.append(line.rstrip('\n'))
        return verbs_que

    def find_children_cite_indexes(self, node):
        """

        :rtype : list
        """
        return [i for i, child in enumerate(node.children) if
                isinstance(child, LabelNode) and
                child.label == 'F-no-c' and
                child.children[0].lemma == '"' and
                i >= 3]

    def get_verb_citing(self, node):
        # Maybe we have more than one verb we are returning the first
        # we find
        for child in node.children:
            if isinstance(child, LabelNode) and child.label == 'verb':
                if child.children[0].lemma in self.verbs_que:
                    return child.children[0].lemma
        return

    def lowered_text_except_properNouns(self, node):
        result_text = ''
        for leaf in node.leaves():
                if leaf.msi['category'] == 'noun':
                    result_text += leaf.original_lexical_form.replace('_', ' ') + " "
                else:
                    result_text += leaf.original_lexical_form.lower() + " "
        return result_text.strip()

    def rewrite(self, sentence, node):
        if self.applies_segun_inicial(sentence, node):
            return self.rewrite_segun_inicial(sentence, node)

    def rewrite_segun_inicial(self, sentence, node):

        text = sentence.paragraph.text.decode("utf-8")

        cite_indexes = self.find_children_cite_indexes(node)

        cite = text[node.children[cite_indexes[0]].token.start():node.children[cite_indexes[1]].token.end()].strip()

        verb = text[node.children[1].token.start():node.children[1].token.end()].strip()

        sn = self.lowered_text_except_properNouns(node.children[0])

        rewritten_sentence = cite + ', ' + verb + " " + sn + "."

        return Rewrite(node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"
