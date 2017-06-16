# -*- coding: utf-8 -*-
from src.rewrite.strategy.textualCite import TextualCite


class QuoteFinder:
    def __init__(self, analysis):
        self.analysis = analysis
        self.textual_cite = TextualCite()
        self.verbs_que = self.textual_cite.verbs_que

    def get_quotes(self):
        quotes = []
        for a_sentence in self.analysis["paragraph"].sentences:
            if self.textual_cite.applies_to(a_sentence, a_sentence.parse_node):
                sentence_quote = self.get_quote(a_sentence)
                quotes.append(sentence_quote)
        return quotes

    def get_quote(self, sentence):
        node = sentence.parse_node
        text = sentence.paragraph.text.decode("utf-8")
        if node.label == "F-no-c":
            closing_quote_idxs = self.textual_cite.find_quote_comma(node)
            closing_quote_idx = closing_quote_idxs[0]
            quote_text = text[node.children[0].token.start():node.children[closing_quote_idx].token.end()].strip()
            quote = {'text': quote_text, 'is_fact': sentence.main_clause().is_fact()}
        else:
            quote_indexes = self.textual_cite.find_children_cite_indexes(node)
            quote_text = text[node.children[quote_indexes[0]].token.start():node.children[quote_indexes[1]].token.end()].strip()
            quote = {'text': quote_text, 'is_fact': sentence.clauses_of_level(1)[0].is_fact()}
        return quote

    def get_checkable_quotes(self):
        final_text = ""
        for a_quote in self.get_quotes():
            if a_quote['is_fact']:
                final_text += a_quote['text'].encode('utf-8') + "\n"

        return final_text.strip()


# from src.model.sentilecto import Sentilecto
# test = Sentilecto.analyze('Alexis dijo: "Cuando vimos eso, debimos correr mucho"')
# print QuoteFinder(test).get_checkable_quotes()
