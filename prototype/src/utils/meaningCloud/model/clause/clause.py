# -*- coding: utf-8 -*-
from src.utils.meaningCloud.model.entity.verb import Verb

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
        self.subject = None
        self.object = None
        self._remove_from_parent()

    def _remove_from_parent(self):
        if self.is_valid and self.parent is not None and self.text in self.parent.text:
            self.parent.text = self.parent.text.replace(self.text, '')

    def _get_text(self):
        if 'form' in self.root:
            return self.root['form']

    def set_info(self):
        if self.subject is None:
            self.subject = self._get_subject()
        if self.object is None:
            self.object = self._get_object()

    def _get_verb(self):
        if 'analysis_list' in self.root:
            for an_item in self.root['analysis_list']:
                text_tags = list(an_item['tag'].replace('-', ''))
                if all(a_tag in text_tags for a_tag in 'V'.split()) and 'F' not in text_tags and 'G' not in text_tags:
                    new_verb = Verb(root=self.root, parent=self.parent)
                    if self.parent is not None:
                        self.parent.verb = new_verb
                        self.parent.subject = self.parent._get_subject()
                        return new_verb
        return None

    def _get_subject(self):
        final_verb = self.verb
        if self.parent is not None:
            final_verb = self.parent.verb

        candidate_type = "iof_isSubject"
        is_passive = (final_verb is not None and final_verb.voice == u'passive')
        if is_passive:
            candidate_type = "iof_isAgentComplement"

        if 'syntactic_tree_relation_list' in self.root:
            for a_relation in self.root['syntactic_tree_relation_list']:
                if a_relation['type'] == candidate_type:
                    if 'form' in self.global_map[a_relation['id']]:
                        subject_text = self.global_map[a_relation['id']]['form'].replace('por', '').strip()
                        if self.parent is not None:
                            self.parent.subject = subject_text.encode('utf-8')
                        return subject_text

        return None

    def _get_object(self):
        final_verb = self.verb
        if self.parent is not None:
            final_verb = self.parent.verb

        candidate_type = "iof_isDirectObject"
        is_passive = (final_verb is not None and final_verb.voice == u'passive')
        if is_passive:
            candidate_type = "iof_isSubject"

        if 'syntactic_tree_relation_list' in self.root:
            for a_relation in self.root['syntactic_tree_relation_list']:
                if a_relation['type'] == candidate_type:
                    if 'form' in self.global_map[a_relation['id']]:
                        object_text = self.global_map[a_relation['id']]['form']
                        if self.parent is not None:
                            self.parent.object = object_text.encode('utf-8')
                        return object_text

        return None

    def __repr__(self):
        return self.text.encode('utf-8')
