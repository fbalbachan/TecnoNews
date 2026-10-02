# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.parser.labelNode import LabelNode
from src.utils.configProvider import ConfigProvider
from src.rewrite.strategy.textualCite import TextualCite
from src.model.tokenization.token import Token

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
        self.textual_cite = TextualCite()

    def applies_to(self, sentence, node):
        return (not self.textual_cite.applies_to(sentence, node)) and self.applies_quote(sentence, node)

    def applies_quote(self, sentence, node):
        verb_que_idx = None
        group_verb_que_idx = None
        closing_quote_idx = None
        is_verb_son_of_verb_root = None

        que_indexes = self.find_children_que(node)

        verbs_que_idx = None
        if isinstance(node, LabelNode):
            if node.label in self.head_nodes:
                verbs_que_idx = self.get_verbs_que_idx_list(node)

                if len(verbs_que_idx) > 0:
                    verb_que_idx = verbs_que_idx[0]

        applies_normal = isinstance(node, LabelNode) \
            and node.label in self.head_nodes \
            and verb_que_idx is not None \
            and len(que_indexes) > 0 \
            and isinstance(node.children[que_indexes[0]], LabelNode) \
            and que_indexes[0] > 1 \
            and (abs(verb_que_idx - que_indexes[0]) < 10) \
            and self.sentence_has_cite(sentence)

        return applies_normal

    def sentence_has_cite(self, sentence):
        for a_clause in sentence.clauses:
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

    def rewrite(self, sentence, node):
        text = sentence.paragraph.text

        spoke_person = None
        a_subject = None
        for a_clause in sentence.clauses:
            if a_clause.verb and a_clause.verb.lemma() in self.verbs_que:
                if a_clause.has_structure("subject"):
                    spoke_person = str(a_clause.structure("subject").entity().referent.designated_ref())
                    a_subject = a_clause.structure("subject").entity()
                    break

        que_index = self.find_children_que(node)[0]
        quote_text = text[node.children[que_index].children[0].token.end():node.token.end()].strip()

        if not spoke_person:
            return None

        quote_token = Token()
        quote_token.components.append((node.children[que_index].children[0].token.end(), node.token.end()))
        prior_to_sentence_token = Token()
        prior_to_sentence_token.components.append((0, sentence.token.start()))
        posterior_to_sentence_token = Token()
        posterior_to_sentence_token.components.append((sentence.token.end(), len(text)))

        to_delete_list = [node.children[que_index].children[0].token, quote_token, a_clause.verb.token, prior_to_sentence_token, posterior_to_sentence_token]
        if not a_subject.is_tacit():
            to_delete_list.append(a_subject.token)
        to_delete_list.sort(key=lambda x: x.start(), reverse=True)

        chorizo = text
        for a_deletable_text in to_delete_list:
            chorizo = (chorizo[:a_deletable_text.start()].strip() + " " + chorizo[a_deletable_text.end():].strip()).strip()

        # print chorizo
        # print spoke_person
        # print a_clause.verb.lexical_form
        quote_text = quote_text[:1].upper() + quote_text[1:]

        if quote_text[-1] in [".", ":", ";"]:
            quote_text = quote_text[:-1]

        rewritten_sentence = chorizo + " " + a_clause.verb.lexical_form + ": \"" + quote_text.strip() + "\"."
        if a_subject.is_linked() or not a_subject.is_tacit():
            rewritten_sentence = a_subject.referent.name().strip() + " " + rewritten_sentence

        return Rewrite(node, rewritten_sentence)

    def find_children_que(self, node):
        """

        :rtype : list
        """
        if not node:
            return []

        return [i for i, child in enumerate(node.children) if
                isinstance(child, LabelNode) and
                (child.label == 'subord' or child.label == 'conj-subord') and
                child.leaves()[0].lemma == 'que']

    @property
    def _get_verbs_que(self):
        """
        load resource list of verbs que

        :return: list of words as list
        """
        verbs_que = []
        config = ConfigProvider()
        verbs_que_filename = config.get("resources", "verbs_que")

        for line in open(verbs_que_filename, 'r', encoding="utf-8"):
            if line[0] not in ['<', '%', '\n']:
                verbs_que.append(line.rstrip('\n'))
        return verbs_que

    def get_verbs_que_idx_list(self, node):
        return [i for i, child in enumerate(node.children) if
                isinstance(child, LabelNode) and
                child.label == 'verb' and child.leaves()[-1].lemma in self.verbs_que]

    type = "dislocation"

# from src.model.sentilecto import Sentilecto
# test = Sentilecto.analyze('''El ministro dijo ayer que existen muchas familias en la Argentina para las que hay buenas oportunidades.
# La Argentina y conquista del Río de la Plata es un poema épico escrito por el arcediano español Martín del Barco Centenera publicado en 1602.''')
# strategy = IndirectToDirectCite()
# for a_sentence in test['paragraph'].sentences:
#     print a_sentence
#     if strategy.applies_to(a_sentence, a_sentence.parse_node):
#         print "APPLIES"
#         print strategy.rewrite(a_sentence, a_sentence.parse_node)
