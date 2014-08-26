# -*- coding: utf-8 -*-
from re import match

from src.model.tokenization.token import Token


class TokenizationGuesser:
    def __init__(self, sentence):
        self.sentence = sentence

    def guess(self):
        text = self.sentence.text.decode("utf-8")
        leaves = self.sentence.parse_node.leaves()

        leaves_it = iter(leaves)
        leaf = None
        token = None
        words = []

        index = 0

        while text:
            if not words:
                if leaf: leaf.token = token
                leaf = leaves_it.next()
                token = Token()
                words = self.words_for(leaf)

            word = words.pop()

            if text.startswith(word):
                length = len(word)
                token.components.append((index, index + length))
                text = text[len(word):]
            else:
                whitespace = match("\s+", text)
                if not whitespace: raise Exception("Tokenization error!")
                words.append(word)

                length = len(whitespace.group(0))
                text = text[length:]

            index += length

        leaf.token = token

    def words_for(self, leaf):
        words = list(leaf.original_components())
        words.reverse()
        return [ word.decode("utf-8") for word in words ]