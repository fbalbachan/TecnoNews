# -*- coding: utf-8 -*-

class Referent:
    def __init__(self, entity):
        self.references = set([ entity ])

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
        return [ repr(reference.kernel if not reference.is_tacit() and reference.kernel else reference)
                for reference in self.references ]

    def ref_count_of(self, name):
        return self.name_list().count(name)

    def name(self):
        designated = self.designated_ref()
        names = []
        for attr in ["names", "surnames"]:
            if designated.has_attr(attr): names.append(designated.attributes[attr][0])
        if not names: names.append(designated.lexical_form)
        return " ".join(names)

    def ref_count(self):
        return len(self.references)

    def __repr__(self):
        return self.name() + " [" + str(self.ref_count()) + "] (" + \
            ", ".join([ str(ref) for ref in self.references ]) + ")"