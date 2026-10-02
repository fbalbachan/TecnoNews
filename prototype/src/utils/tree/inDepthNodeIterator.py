# -*- coding: utf-8 -*-


class InDepthNodeIterator:
    def __init__(self, node, banned_nodes=[]):
        self.banned_nodes = banned_nodes
        self.node_stack = []
        if not self.is_banned(node):
            self.node_stack.append(node)

    def __next__(self):
        if not self.node_stack:
            raise StopIteration
        else:
            node = self.node_stack.pop()
            non_banned_nodes = self.non_banned_nodes(node.children[::-1])
            self.node_stack.extend(non_banned_nodes)
            return node

    def non_banned_nodes(self, nodes):
        return [node for node in nodes if not self.is_banned(node)]

    def is_banned(self, node):
        return node in self.banned_nodes

    def __iter__(self):
        return self