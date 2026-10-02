# -*- coding: utf-8 -*-


class Object(object):
    def __init__(self, root, is_passive=False):
        self.root = root
        self.lemma = None
        self.lexical_form = None
        self.tag = None
        self.is_passive = is_passive
        self.is_proper_noun = False
        self._set_info()

    def _set_info(self):
        if 'analysis_list' in self.root:
            for an_item in self.root['analysis_list']:
                if 'lemma' in an_item:
                    self.lemma = an_item['lemma']
                if 'original_form' in an_item:
                    self.lexical_form = an_item['original_form']
                    if self.is_passive and len(self.lexical_form.split(' ')) > 1:
                        self.lexical_form = ' '.join(self.lexical_form.split(' ')[1:])

                if 'tag' in an_item:
                    tag_set = list(an_item['tag'])
                    self.tag = tag_set

        stack = [self.root]
        while len(stack) > 0:
            current_element = stack.pop()
            if 'analysis_list' in current_element:
                for an_item in current_element['analysis_list']:
                    if 'tag' in an_item:
                        tag_set = list(an_item['tag'])
                        if len(tag_set) > 2 and tag_set[0] == 'N' and tag_set[1] == 'P':
                            self.is_proper_noun = True
                            return
            if 'token_list' in current_element:
                for a_token in current_element['token_list']:
                    stack.append(a_token)

    def __repr__(self):
        return "%s - Is proper noun: %s" % (self.lexical_form, str(self.is_proper_noun))
