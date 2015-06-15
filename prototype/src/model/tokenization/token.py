# -*- coding: utf-8 -*-


class Token:
    def __init__(self):
        self.components = []

    def append(self, start, end):
        self.components.append((start, end))
        self.components.sort(key=lambda (p_start, p_end): p_start)

    def start(self):
        return self.components[0][0]

    def end(self):
        return self.components[-1][1]

    def overlaps(self, other):
        return bool(set(range(self.start(), self.end())) & set(range(other.start(), other.end())))

    def __repr__(self):
        return "(" + str(self.start()) + ", " + str(self.end()) + ")"