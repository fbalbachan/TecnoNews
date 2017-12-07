# -*- coding: utf-8 -*-
from collections import deque, Iterable
from src.utils.meaningCloud.sentenceExtractor import SentenceExtractor
from src.utils.meaningCloud.clauseExtractor import ClauseExtractor
import json


class TreeRepresentation(object):
    def __init__(self, a_tree):
        self.tree = a_tree
        self.sentences = []
        self.clauses = []
        self.global_map = {}
        #self.print_tree()
        #exit()

        self._build_map()


        #print '\n'.join(self.get_compliance())
        return
        exit()
        print self.sentences
        for a_clause in self.clauses:
            print a_clause['text']
        exit()


    def get_compliance(self):
        sentences = SentenceExtractor(self.global_map).extract()
        ClauseExtractor(self.global_map, sentences).extract()
        result = []
        actions = ['estafar', 'defraudar', 'quebrar', 'evadir', 'sobornar', 'coimear']
        for a_sentence in sentences:
            for a_clause in a_sentence.clauses:
                if a_clause.verb is not None and a_clause.verb.lower() in actions:
                    result.append("FINANCIAL COMPLIANCE DETECTED")
                result.append(repr(a_clause))
                result.append(repr(a_clause.subject))
                result.append(repr(a_clause.verb))
                result.append("------------")
        return result

    def print_tree(self):
        full_dict = {}
        clause_hierarchy = {}
        sentences = {}
        stack = deque()
        if 'token_list' in self.tree:
            for a_node in reversed(self.tree['token_list']):
                stack.append({'node': a_node, 'level': 0, 'parentId': -1})
                sentences[a_node['id']] = {'id': a_node['id'], 'clauses': []}
        while len(stack) > 0:
            current_node = stack.pop()
            an_item = current_node['node']

            full_dict[an_item['id']] = {'node': an_item, 'isValid': False, 'parentId': current_node['parentId'], 'level': current_node['level']}

            if 'token_list' in an_item:
                for a_sub_item in reversed(an_item['token_list']):
                    stack.append({'node': a_sub_item, 'level': current_node['level'] + 1, 'parentId': an_item['id']})
            if 'analysis_list' in an_item:
                text_tag = an_item['analysis_list'][0]['tag']
                if len(text_tag) > 0 and text_tag[0] == 'Z':
                    full_dict[an_item['id']]['isValid'] = True
                    clause_hierarchy[an_item['id']] = {'id': an_item['id'], 'clauses': [], 'text': an_item['form']}

        for a_phrase in full_dict.values():
            if not a_phrase['isValid']:
                continue

            predecessor = full_dict[a_phrase['parentId']]
            valid_pred = (predecessor['level'] == 0 or predecessor['isValid'])
            while not valid_pred:
                predecessor = full_dict[predecessor['parentId']]
                valid_pred = (predecessor['level'] == 0 or predecessor['isValid'])

            if predecessor['node']['id'] in sentences:
                sentences[predecessor['node']['id']]['clauses'].append(clause_hierarchy[a_phrase['node']['id']])
            else:
                clause_hierarchy[predecessor['node']['id']]['clauses'].append(clause_hierarchy[a_phrase['node']['id']])

            an_item = a_phrase['node']
            indentation = u""
            for i in range(a_phrase['level']):
                indentation += u"    "
            print indentation + " " + unicode(an_item['id']) + " " + an_item['form'] + " " + a_phrase['parentId']


        sentences = [sentences[a_key] for a_key in sorted(sentences.iterkeys())]

        # SORT ALL COMPONENTS
        unsorted_lists = [sentences]
        while len(unsorted_lists) > 0:
            current_list = unsorted_lists.pop()
            current_list.sort(key=lambda x: x['id'], reverse=False)
            for an_elem in current_list:
                if len(an_elem['clauses']) > 0:
                    unsorted_lists.append(an_elem['clauses'])



        offences = ['corrupción', 'droga', 'narcotráfico', 'narcotraficante', 'narcótico',  'estupefaciente', 'terrorismo', 'peculado', 'enriquecimiento', 'estafa', 'fraude', 'defraudación', 'quiebra', 'acreedor', 'deuda', 'embargo', 'contrabando' 'soborno', 'evasión', 'cohecho', 'coima']
        actions = ['estafar', 'defraudar', 'quebrar', 'evadir', 'sobornar', 'coimear']
        for a_clause in clause_hierarchy.keys():
            result = self.contains_tag('V', full_dict[a_clause]['node'])
            if result is None:
                continue

            if result[0] in actions:
                print "\n\n\n"
                print result[0]
                if result[1] is not None:
                    found = False
                    for a_relation in result[1]:
                        if a_relation['type'] == "iof_isSubject":
                            for a_token in full_dict[a_relation['id']]['node']['token_list']:
                                if 'analysis_list' in a_token:
                                    for an_analysis in a_token['analysis_list']:
                                        if 'propio' in an_analysis['tag_info']:
                                            print "PASA"
                                            print "----------"
                                            print full_dict[a_relation['id']]['node']['form']
                                            print "---------"
                            found = True
                    if not found:
                        print "NO TIENE SUBJECT"


                else:
                    print "NO TIENE SYNTACTIC"

                print clause_hierarchy[a_clause]['text']
        # print json.dumps(sentences, sort_keys=True, indent=4)

    def contains_tag(self, tag, tree):
        if 'analysis_list' in tree:
            for an_item in tree['analysis_list']:
                text_tags = list(an_item['tag'].replace('-', ''))
                if all(a_tag in text_tags for a_tag in tag.split()) and 'F' not in text_tags:
                    #print an_item['tag_info']
                    if 'syntactic_tree_relation_list' not in tree:
                        return (an_item['lemma'], None)
                    else:
                        if any(a_syntactic['type'] == 'iof_isAgentComplement' for a_syntactic in tree['syntactic_tree_relation_list']):
                            return None
                        return (an_item['lemma'], tree['syntactic_tree_relation_list'])

        if 'token_list' in tree:
            for a_token in tree['token_list']:
                sub_result = self.contains_tag(tag, a_token)
                if sub_result is not None:
                    return sub_result
        return None

    def _build_map(self):
        queue = deque()
        if 'token_list' in self.tree:
            queue.appendleft(self.tree['token_list'])

        while len(queue) > 0:
            current_part = queue.pop()
            for an_elem in current_part:
                if 'id' in an_elem:
                    self.global_map[an_elem['id']] = an_elem
                if 'token_list' in an_elem:
                    queue.appendleft(an_elem['token_list'])

                '''
                if 'type' in an_elem:
                    if an_elem['type'] == 'sentence' and 'id' in an_elem and 'token_list' in an_elem:
                        self.sentences.append({'id': int(an_elem['id']), 'text': self._get_raw_text(an_elem['token_list'])})

                        for a_sub_sentence in an_elem['token_list']:
                            self.clauses.extend(self._extract_clauses(a_sub_sentence))
                '''

    def _extract_clauses(self, a_sentence):
        clauses = []
        partial_clause = None
        if 'token_list' in a_sentence:
            for a_part in a_sentence['token_list']:
                if 'analysis_list' in a_part:
                    text_tag = a_part['analysis_list'][0]['tag']
                    if len(text_tag) > 1 and text_tag[0] == 'Z' and text_tag[1] != '-':
                        if partial_clause is not None:
                            clauses.append(partial_clause)
                            partial_clause = None
                        clauses.append({'text': self._get_raw_text([a_part]), 'ids': [a_part['id']]})
                    else:
                        if partial_clause is None:
                            partial_clause = {'text': '', 'ids': []}
                        partial_clause['text'] += ' ' + self._get_raw_text([a_part])
                        partial_clause['text'] = partial_clause['text'].strip()
                        partial_clause['ids'].append(a_part['id'])
            if partial_clause is not None:
                clauses.append(partial_clause)
        return clauses

    def _get_raw_text(self, an_elem):
        resulting_text = u""
        if isinstance(an_elem, Iterable):
            for a_sub_elem in an_elem:
                if 'form' in a_sub_elem:
                    resulting_text += a_sub_elem['form']
        return resulting_text

    def get_sentences(self, a_tree):
        sentences = []
        queue = deque()

        if 'token_list' in a_tree:
            queue.appendleft(a_tree['token_list'])

        while len(queue) > 0:
            current_list = queue.pop()
            for an_elem in current_list:
                if 'type' in an_elem and an_elem['type'] == 'sentence':
                    sentences.append(an_elem)
                if 'token_list' in an_elem:
                    queue.appendleft(an_elem['token_list'])

        for a_sentence in sentences:
            if 'token_list' in a_sentence:
                for a_component in a_sentence['token_list']:
                    if 'token_list' in a_component:
                        del(a_component['token_list'])
        return sentences
