# -*- coding: utf-8 -*-


class Sentence(object):
    def __init__(self, root):
        self.root = root
        self.text = self._get_text()
        self.clauses = []
        self.invalid_clauses = []
        self.id = self.root['id'] if 'id' in self.root else -1

    def _get_text(self):
        if 'token_list' in self.root:
            tokens = [a_token['form'] for a_token in self.root['token_list'] if 'form' in a_token]
            return ''.join(tokens)

    def __repr__(self):
        return self.text
