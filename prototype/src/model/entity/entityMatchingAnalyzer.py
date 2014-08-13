# -*- coding: utf-8 -*-

class EntityMatchingAnalyzer:
    def __init__(self, source):
        self.source = source

    def matches(self, other):
        #if self.source.classification() != other.classification(): return False
        methods = [ self.whole_lexical_form, self.same_kernel, self.same_name_or_surname ]
        return any(( method(other) for method in methods ))

    def whole_lexical_form(self, other):
        source_form = self.source.lexical_form.lower()
        return source_form == other.lexical_form.lower()

    def same_kernel(self, other):
        source = self.source
        if source.classification() and source.classification() == other.classification():
            return source.kernel.lexical_form == other.kernel.lexical_form
        return False

    def same_name_or_surname(self, other):
        source = self.source
        print "source", source, source.attributes, " - other", other, other.attributes
        if source.classification() == "person" and source.classification() == other.classification():
            match = False
            for attr in ["names", "surnames"]:
                if source.has_attr(attr) and other.has_attr(attr):
                    attr_match = source.attributes[attr][0] == other.attributes[attr][0]
                    if not attr_match: return False
                    match = match or attr_match
            return match
        return False