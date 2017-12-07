# -*- coding: utf-8 -*-


class Clause(object):
    def __init__(self, root, sentence, global_map, parent=None, is_valid=False,):
        self.root = root
        self.global_map = global_map
        self.text = self._get_text()
        self.sentence = sentence
        self.parent = parent
        self.children = []
        self.invalid_children = []
        self.is_valid = is_valid
        self.id = self.root['id'] if 'id' in self.root else -1
        self.verb = self._get_verb()
        self.subject = self._get_subject()
        self._remove_from_parent()

    def _remove_from_parent(self):
        if self.is_valid and self.parent is not None and self.text in self.parent.text:
            self.parent.text = self.parent.text.replace(self.text, '')

    def _get_text(self):
        if 'form' in self.root:
            return self.root['form']

    def _get_verb(self):
        if 'analysis_list' in self.root:
            for an_item in self.root['analysis_list']:
                text_tags = list(an_item['tag'].replace('-', ''))
                if all(a_tag in text_tags for a_tag in 'V'.split()) and 'F' not in text_tags:
                    if self.parent is not None:
                        self.parent.verb = an_item['lemma'].encode('utf-8')
                        return an_item['lemma']
        return None

    def _get_subject(self):
        if 'syntactic_tree_relation_list' in self.root:
            for a_relation in self.root['syntactic_tree_relation_list']:
                if a_relation['type'] == "iof_isSubject":
                    if 'form' in self.global_map[a_relation['id']]:
                        subject_text = self.global_map[a_relation['id']]['form']
                        if self.parent is not None:
                            self.parent.subject = subject_text.encode('utf-8')
                        return subject_text
        return None

    def __repr__(self):
        return self.text.encode('utf-8')
