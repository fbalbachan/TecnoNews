from src.rewrite.rewrite import Rewrite
from src.parser.labelNode import LabelNode
from src.utils.configProvider import ConfigProvider

debug_mode = False


class IndirectToDirectCite:
    def __init__(self, dislocation=None, changes=None):
        if dislocation is None:
            self.dislocation = [True, False]

        # TODO: fixme why we use this value on changes? which value should we use?
        # if changes is None:
        #     self.changes = ["de_acuerdo_con", ""]

        self.verbs_que = self._get_verbs_que
        self.head_nodes = ["grup-verb", "subord-rel", "subord", "subord-ger", "verb-pass"]

    def applies_to(self, sentence, node):
        return self.applies_quote(sentence, node)

    def applies_quote(self, sentence, node):
        verb_que_idx = None
        group_verb_que_idx = None
        closing_quote_idx = None
        is_verb_son_of_verb_root = None

        que_indexes = self.find_children_que(node)

        if isinstance(node, LabelNode):
            if node.label in self.head_nodes:
                verbs_que_idx = self.get_verbs_que_idx_list(node)

                if len(verbs_que_idx) > 0:
                    verb_que_idx = verbs_que_idx[0]

        applies_normal = isinstance(node, LabelNode) \
            and node.label in self.head_nodes \
            and verb_que_idx \
            and len(que_indexes) > 0 \
            and isinstance(node.children[que_indexes[0]], LabelNode) \
            and que_indexes[0] > 1 \
            and (abs(verb_que_idx - que_indexes[0]) < 10)

        return applies_normal

    def find_children_que(self, node):
        """

        :rtype : list
        """
        if not node:
            return []

        return [i for i, child in enumerate(node.children) if
                isinstance(child, LabelNode) and
                (child.label == 'subord' or child.label == 'conj-subord') and
                child.children[0].lemma == 'que']

    @property
    def _get_verbs_que(self):
        """
        load resource list of verbs que

        :return: list of words as list
        """
        verbs_que = []
        config = ConfigProvider()
        verbs_que_filename = config.get("resources", "verbs_que")

        for line in open(verbs_que_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                verbs_que.append(line.rstrip('\n'))
        return verbs_que

    def get_verbs_que_idx_list(self, node):
        return [i for i, child in enumerate(node.children) if
                isinstance(child, LabelNode) and
                child.label == 'verb' and child.leaves()[-1].lemma in self.verbs_que]
