# -*- coding: utf-8 -*-
from collections import deque
from re import compile, IGNORECASE, UNICODE

from src.model.tokenization.token import Token
from src.utils.stringUtils import remove_accents

debug_mode = False

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

        index = self.sentence.token.start()


        following_contraction = []
        mismatchs = deque()

        #ALEXIS: I had to append items to it while processing (is it possible to do that to an iterator??)
        leaves_lst = list(leaves_it)
        list_len = len(leaves_lst) #Failsafe limit to avoid endless loop
        moved_leaves = 0

        while text:
            if not words:
                if leaf:
                    leaf.token = token

                #leaf = leaves_it.next()
                leaf = leaves_lst.pop(0) #ALEXIS: Same behaviour (but with list instead of iter)

                token = Token()
                words = self.words_for(leaf)

            if debug_mode: print "REMAINING WORDS: "
            if debug_mode: print words

            word = words.pop()

            if debug_mode: print "-------------CURRENT WORD: " + word.encode('utf-8')

            if not following_contraction:
                following_contraction = self.get_following_contraction(text)

            if following_contraction:
                if debug_mode: print "HAS FOLLOWING CONTRACTION"
                component = following_contraction.popleft()
                if component[0] == word.lower():
                    word = component[1] if component[1] != word.lower() else word
                else:
                    following_contraction = []

            if debug_mode: print "WORD AFTER CONTRACTIONS:" + word.encode('utf-8')

            if self.starts_with(word, text):
                if debug_mode: print "STARTS WITH"
                length = len(word)
                token.components.append((index, index + length))
                text = text[len(word):]
            elif self.is_pending_mismatch(word, mismatchs):
                if debug_mode: print "IS PENDING MISSMATCH"
                mismatch, mismatch_index = mismatchs.popleft()
                token.components.append((mismatch_index, mismatch_index + len(mismatch)))
                length = 0
            else:
                match = self.whitespace_pattern.match(text)
                if not match:
                    if debug_mode: print "NOT WHITESPACE"
                    match = self.mismatch_pattern.match(text)
                    if not match:
                        if debug_mode: print "NOT MISSMATCH"
                        #text = text if not isinstance(text, unicode) else text.encode("utf8")
                        #word = word if not isinstance(word, unicode) else word.encode("utf8")

                        #bad_word_index = self.sentence.text.find(word,index)
                        #sentence_start = self.sentence.text[:bad_word_index]
                        #sentence_end = self.sentence.text[bad_word_index+len(word):]

                        #fixed_text = sentence_start + sentence_end

                        leaves_lst.append(leaf) #Move leaf at the end of the list
                        words = []

                        #Avoid endless loop if unexpected case (It would deep moving the same leaves endlessly)
                        if moved_leaves > list_len:
                            if debug_mode: print "MOVE LIMIT! BREAK>>>>>>>>>>>>>>>>>>>>>>>>>>"
                            break
                        moved_leaves = moved_leaves +1

                        if debug_mode: print "CONTINUE"
                        continue

                        #break
                        #msg = ("Tokenization error! Text: [%s] - Word: [%s]" % (text, word))
                        #raise Exception(msg, fixed_text)

                    mismatchs.append((match.group(0), index))
                moved_leaves = 0
                words.append(word)

                length = len(match.group(0))
                text = text[length:]

            if debug_mode: print "TEXT AFTER CHANGES: " + text.encode('utf-8')

            index += length

            if debug_mode: print "NEW LENGTH: " + str(length)

        leaf.token = token

        for word, index in mismatchs:
            token = Token()
            token.components.append((index, index + len(word)))

            leaf = leaves_it.next()
            leaf_word = leaf.original_lexical_form.decode("utf-8")

            if leaf_word != word:
                raise Exception("Tokenization error!")
            leaf.token = token

        self.assing_middle_node_tokens()

    def assing_middle_node_tokens(self):
        try:
            for node in [ node for node in self.sentence.parse_node if not node.is_leaf() ]:
                token = Token()
                token.components = [ (leaf.token.start(), leaf.token.end()) for leaf in node.leaves() ]
                node.token = token
        except:
            print "TOKENIZATION ERROR!"

    def is_pending_mismatch(self, word, mismatchs):
        if not mismatchs:
            return False
        return mismatchs[0][0] == word

    def get_following_contraction(self, text):
        match = self.contraction_pattern.match(text)
        if not match:
            return []

        word = match.group(0).lower()
        return deque(self.contractions[word])

    def starts_with(self, word, text):
        if len(text) < len(word):
            return False
        prefix = text[:len(word)]
        return remove_accents(prefix) == remove_accents(word)

    def words_for(self, leaf):
        words = list(leaf.original_components())
        words.reverse()
        return [word.decode("utf-8") for word in words]

    contractions = {"al": [("a", "a"), ("el", "l")],
                    "del": [("de", "de"), ("el", "l")]}
    contraction_pattern = compile("al|del", IGNORECASE)

    # mismatch_pattern = compile("\w+|[,]", UNICODE)
    mismatch_pattern = compile('[",]', UNICODE)
    whitespace_pattern = compile("\s+")
