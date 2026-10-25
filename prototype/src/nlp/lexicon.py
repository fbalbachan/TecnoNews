# -*- coding: utf-8 -*-
"""FreeLing's own Spanish lexical resources, bundled in resources/:

    freeling_es.dic          form lemma tag [lemma tag ...]   (FreeLing morphological dictionary)
    locucions_extended.dat   multiword expressions            (FreeLing locutions: pese_a, lo_cual...)

spaCy decides the part of speech and the syntax; these resources give the words the exact lemmas,
EAGLES tags and multiword units that FreeLing produced, which is what the linguistic model expects.
"""
import io
import os
import re

from src.ling import msi_data

DEFAULT_DICTIONARY = "resources/freeling_es.dic"
DEFAULT_LOCUTIONS = "resources/locucions_extended.dat"

_instance = []


def get_lexicon():
    if not _instance:
        _instance.append(Lexicon(*_resource_paths()))
    return _instance[0]


def _resource_paths():
    try:
        from src.utils.configProvider import ConfigProvider
        config = ConfigProvider()
        return config.get("resources", "freeling_dict"), config.get("resources", "locutions")
    except Exception:
        return DEFAULT_DICTIONARY, DEFAULT_LOCUTIONS


def valid_tag(tag):
    """Same checks as src.ling.msi_mapper.tag_to_full_msi, without raising."""
    try:
        category = tag[0]
        attributes = msi_data.attribute_map[category]
        if category == "N":
            for position, letter in zip([1, 2, 3, 45, 6], [tag[1], tag[2], tag[3], tag[4:6], tag[6]]):
                attributes[position][1][letter]
        elif category == "F":
            attributes[tag[1:]]
        else:
            for position, letter in enumerate(tag[1:], 1):
                attributes[position][1][letter]
        return len(tag) <= 8
    except (KeyError, IndexError):
        return False


class Lexicon(object):
    def __init__(self, dictionary_path, locutions_path):
        self._forms = {}
        self.locutions_by_form = {}
        self.locutions_by_lemma = {}
        if dictionary_path and os.path.exists(dictionary_path):
            self._load_dictionary(dictionary_path)
        if locutions_path and os.path.exists(locutions_path):
            self._load_locutions(locutions_path)

    # dictionary ----------------------------------------------------------------------------------

    def _load_dictionary(self, path):
        # kept as utf-8 bytes: half a million entries
        with io.open(path, "rb") as dictionary:
            for line in dictionary:
                line = line.strip()
                space = line.find(b" ")
                if space > 0:
                    self._forms[line[:space]] = line[space + 1:]

    def analyses(self, form):
        """[(lemma, tag)] for a word form, as listed in the FreeLing dictionary."""
        raw = self._forms.get(form.lower().encode("utf-8"))
        if raw is None:
            return []
        tokens = raw.decode("utf-8").split()
        return [(lemma, tag) for lemma, tag in zip(tokens[0::2], tokens[1::2])
                if "+" not in lemma and valid_tag(tag)]

    # locutions -----------------------------------------------------------------------------------

    def _load_locutions(self, path):
        with io.open(path, encoding="utf-8") as locutions:
            for line in locutions:
                fields = line.split()
                if len(fields) < 3:
                    continue
                components = re.findall(r"<[^>]*>|[^_]+", fields[0])
                parsed = []
                for component in components:
                    if component.startswith("<"):
                        if "_" in component:
                            parsed = None
                            break
                        parsed.append(("lemma", component[1:-1].lower()))
                    else:
                        parsed.append(("form", component.lower()))
                if not parsed or len(parsed) < 2:
                    continue
                locution = (tuple(parsed), fields[1], fields[2])
                kind, value = parsed[0]
                index = self.locutions_by_form if kind == "form" else self.locutions_by_lemma
                index.setdefault(value, []).append(locution)

    def locutions_starting_with(self, form, lemmas):
        found = list(self.locutions_by_form.get(form.lower(), []))
        for lemma in lemmas:
            found.extend(self.locutions_by_lemma.get(lemma, []))
        return found
