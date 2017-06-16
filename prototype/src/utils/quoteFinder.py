# -*- coding: utf-8 -*-
from src.rewrite.strategy.textualCite import TextualCite
from src.rewrite.strategy.indirectToDirectCite import IndirectToDirectCite


class QuoteFinder:
    def __init__(self, analysis):
        self.analysis = analysis
        self.textual_cite = TextualCite()
        self.indirect_textual_cite = IndirectToDirectCite()
        self.verbs_que = self.textual_cite.verbs_que

    def get_quotes(self):
        quotes = []
        for a_sentence in self.analysis["paragraph"].sentences:
            if self.textual_cite.applies_to(a_sentence, a_sentence.parse_node):
                sentence_quote = self.get_quote(a_sentence)
                quotes.append(sentence_quote)
            elif self.indirect_textual_cite.applies_to(a_sentence, a_sentence.parse_node):
                sentence_quote = self.get_indirect_quote(a_sentence)
                quotes.append(sentence_quote)
        return quotes

    def get_indirect_quote(self, sentence):
        node = sentence.parse_node
        text = sentence.paragraph.text.decode("utf-8")

        spoke_person = "The Author"
        for a_clause in sentence.clauses:
            if a_clause.verb and a_clause.verb.lemma() in self.verbs_que:
                if a_clause.has_structure("subject"):
                    spoke_person = str(a_clause.structure("subject").entity().referent.designated_ref())
                    break

        que_index = self.indirect_textual_cite.find_children_que(node)[0]
        quote_text = text[node.children[que_index].children[0].token.end():node.token.end()].strip()
        quote = {'text': quote_text.encode('utf-8'), 'is_fact': sentence.clauses_of_level(1)[0].is_fact(), 'spoke_person': spoke_person}
        return quote

    def get_quote(self, sentence):
        node = sentence.parse_node
        text = sentence.paragraph.text.decode("utf-8")
        spoke_person = "The Author"

        if node.label == "F-no-c":
            # print "CASO 1"
            for a_clause in sentence.clauses:
                if a_clause == sentence.main_clause():
                    continue
                if a_clause.verb and a_clause.verb.lemma() in self.textual_cite.verbs_que:
                    if a_clause.has_structure("subject"):
                        spoke_person = str(a_clause.structure("subject").entity().referent.designated_ref())
                        break

            closing_quote_idxs = self.textual_cite.find_quote_comma(node)
            closing_quote_idx = closing_quote_idxs[0]
            quote_text = text[node.children[0].token.start():node.children[closing_quote_idx].token.end()].strip()
            quote = {'text': quote_text.encode('utf-8'), 'is_fact': sentence.main_clause().is_fact(), 'spoke_person': spoke_person}
        else:
            # print "CASO 2"
            if sentence.main_clause().has_structure("subject"):
                spoke_person = str(sentence.main_clause().structure("subject").entity().referent.designated_ref())
            quote_indexes = self.textual_cite.find_children_cite_indexes(node)
            quote_text = text[node.children[quote_indexes[0]].token.start():node.children[quote_indexes[1]].token.end()].strip()
            quote = {'text': quote_text.encode('utf-8'), 'is_fact': sentence.clauses_of_level(1)[0].is_fact(), 'spoke_person': spoke_person}
        return quote

    def get_checkable_quotes(self):
        final_text = ""
        for a_quote in self.get_quotes():
            if a_quote['is_fact']:
                final_text += a_quote['text'] + " (" + a_quote["spoke_person"] + " dixit)" + "\n"

        return final_text.strip()


# from src.model.sentilecto import Sentilecto
# test = Sentilecto.analyze('Stanley sostuvo que "existen un millón y medio de familias que reciben una pensión en la Argentina y que la van a seguir cobrando".')
# print QuoteFinder(test).get_checkable_quotes()
