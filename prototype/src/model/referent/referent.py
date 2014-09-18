# -*- coding: utf-8 -*-

class Referent:
    def __init__(self, entity):
        self.references = set([ entity ])
        self.extra_words = []

    def add_reference(self, entity):
        self.references.add(entity)

    def semantic_classification(self):
        return self.designated_ref().classification()

    def designated_ref(self):
        if all([ not entity.classification() for entity in self.references ]): return next(iter(self.references))
        classified = filter(lambda entity: entity.classification(), self.references)
        named = filter(lambda entity: entity.has_attr("names") or entity.has_attr("surnames"), classified)
        fully_named = filter(lambda entity: entity.has_attr("names") and entity.has_attr("surnames"), named)

        for _list in [ fully_named, named, classified ]:
            if _list: return _list[0]

    def names(self):
        return set(self.name_list())

    def name_list(self):
        return [ reference.name() for reference in self.references ]

    def references_with(self, name):
        return [ reference for reference in self.references if reference.name() == name ]

    def ref_count_of(self, name):
        return self.name_list().count(name)

    def name(self):
        designated = self.designated_ref()
        names = []
        for attr in ["names", "surnames"]:
            if designated.has_attr(attr): names.extend(designated.attributes[attr])
        if not names: names.append(designated.lexical_form)
        return " ".join(names)

    def ref_count(self):
        return len(self.references)

    def explicit_references(self):
        return filter(lambda entity: not entity.is_tacit(), self.references)

    def __repr__(self):
        return self.name() + " [" + str(self.ref_count()) + "] (" + \
            ", ".join([ str(ref) for ref in self.references ]) + ")"