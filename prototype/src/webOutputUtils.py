# -*- coding: utf-8 -*-

class WebOutputUtils:

    def structure(self, clause, name):
        if clause.has_structure(name):
            return ", ".join([ entity.lexical_form for entity in clause.structure(name).all_entities() ])
        else:
            return ""

    def tooltip(self, clause, name):
        if clause.has_structure(name):
            return ", ".join([ self.msi_string(entity.msi) for entity in clause.structure(name).all_entities() ])
        else:
            return ""

    def entity_tooltip(self, entity):
        return self.msi_string(entity.msi)

    def msi_string(self, msi):
        return str(msi["person"]) + "° " + str(msi["gender"]) + " " + str(msi["number"]) + " (" + str(msi["category"]) + ")"
        #return ", ".join([ key + " = " + str(value) for (key, value) in msi.items() ])
