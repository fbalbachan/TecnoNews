# -*- coding: utf-8 -*
from src.utils.meaningCloud.model.clause.clause import Clause
from collections import deque


class ClauseExtractor(object):
    def __init__(self, global_map, sentences):
        self.global_map = global_map
        self.sentences = sentences

    def extract(self):
        stack = deque()
        for a_sentence in self.sentences:
            if 'token_list' in a_sentence.root:
                stack.extend([{'parent': None, 'token': a_token} for a_token in reversed(a_sentence.root['token_list'])])

            while len(stack) > 0:
                current_element = stack.pop()
                current_token = current_element['token']

                is_valid = False
                if 'analysis_list' in current_token:
                    tags = [a_tag['tag'] for a_tag in current_token['analysis_list']]
                    if any(len(a_tag.replace('-', '')) > 0 and a_tag[0] == 'Z' for a_tag in tags):
                        is_valid = True

                new_clause = Clause(root=current_token, sentence=a_sentence, global_map=self.global_map, parent=current_element['parent'], is_valid=is_valid)

                if new_clause.is_valid:
                    a_sentence.clauses.append(new_clause)
                else:
                    a_sentence.invalid_clauses.append(new_clause)

                if 'token_list' in new_clause.root:
                    next_parent = new_clause
                    if not new_clause.is_valid:
                        next_parent = new_clause.parent

                    stack.extend([{'parent': next_parent, 'token': a_token} for a_token in reversed(new_clause.root['token_list'])])

        for a_sentence in self.sentences:
            for a_clause in a_sentence.invalid_clauses:
                a_clause.set_info()
            for a_clause in a_sentence.clauses:
                a_clause.set_info()
                #print a_clause
                #full_dict[an_item['id']] = {'node': an_item, 'isValid': False, 'parentId': current_node['parentId'], 'level': current_node['level']}
