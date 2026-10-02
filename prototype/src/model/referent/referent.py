# -*- coding: utf-8 -*-


class Referent:
    def __init__(self, entity):
        self.references = {entity}
        self.extra_words = []

    def add_reference(self, entity):
        self.references.add(entity)

    def semantic_classification(self):
        return self.designated_ref().classification()

    def designated_ref(self):
        if all([not ref_entity.classification() for ref_entity in self.references]):
            return next(iter(self.references))
        classified = [entity for entity in self.references if entity.classification()]
        named = [c_entity for c_entity in classified if c_entity.has_attr("names") or c_entity.has_attr("surnames")]
        fully_named = [named_entity for named_entity in named if named_entity.has_attr("names")and named_entity.has_attr("surnames")]

        for _list in [fully_named, named, classified]:
            if _list:
                _list = [x for x in _list]
                return _list[0]

    def names(self):
        return set(self.name_list())

    def name_list(self):
        return [reference.name() for reference in self.references]

    def references_with(self, name):
        return [reference for reference in self.references if reference.name() == name]

    def ref_count_of(self, name):
        return self.name_list().count(name)

    def name(self):
        designated = self.designated_ref()
        names = []
        for attr in ["names", "surnames"]:
            if designated.has_attr(attr):
                names.extend(designated.attributes[attr])

        if not names:
            names.append(designated.lexical_form)

        return " ".join(names)

    def ref_count(self):
        return len(self.references)

    def explicit_ref_count(self):
        return len(self.explicit_references())

    def explicit_references(self):
        return [entity for entity in self.references if not entity.is_tacit()]

    def first_occurrence(self):
        return sorted(self.explicit_references(), key = lambda reference: reference.token.start())[0]

    def __repr__(self):
        return self.name() + " [" + str(self.ref_count()) + "] (" + \
            ", ".join([str(ref) for ref in self.references]) + ")"
