# -*- coding: utf-8 -*-


class Verb(object):
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent
        self.lemma = None
        self.lexical_form = None
        self.tag = None
        self.voice = None
        self._set_info()

    def _set_info(self):
        if 'analysis_list' in self.root:
            for an_item in self.root['analysis_list']:
                if 'lemma' in an_item:
                    self.lemma = an_item['lemma']
                if 'original_form' in an_item:
                    self.lexical_form = an_item['original_form']
                if 'tag' in an_item:
                    tag_set = list(an_item['tag'])
                    self.tag = tag_set
                    if tag_set[7] == u'A':
                        self.voice = u'active'
                    elif tag_set[7] == u'P':
                        self.voice = u'passive'


    def __repr__(self):
        return "%s - %s voice" % (self.lemma.encode('utf-8'), self.voice.encode('utf-8'))
