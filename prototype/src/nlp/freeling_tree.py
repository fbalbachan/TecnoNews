# -*- coding: utf-8 -*-
"""spaCy dependency parse -> FreeLing full-parse tree (as printed by FreeLing's analyzer_client).

The whole linguistic model (src/model, src/rewrite) was written against the trees produced by the
FreeLing Spanish chart parser: chunk labels such as grup-verb, verb-pass, sn, grup-sp, sp-de,
subord, subord-rel, subord-ger, patons, coor-n... and EAGLES tags on the leaves. This module rebuilds
that structure from a spaCy (Universal Dependencies) analysis, so the rest of the code keeps working
unchanged. Output example for "Dijo que la amaba.":

    +grup-verb_[
      +verb_[
        +(Dijo decir VMIS3S0 -)
      ]
      subord_[
        +(que que CS -)
        grup-verb_[
          patons_[
            +paton-fs_[
              +(la lo PP3FSA00 -)
      ...
"""
import re
import unicodedata

from src.nlp import eagles
from src.nlp.eagles import CLITIC_PRONOUNS, SEMANTIC_CLASS_BY_ENT
from src.nlp.lexicon import get_lexicon, valid_tag

# --------------------------------------------------------------------------------------------------
# Lexical data
# --------------------------------------------------------------------------------------------------

DAYS_OF_WEEK = {"lunes": "L", "martes": "M", "miércoles": "X", "miercoles": "X", "jueves": "J",
                "viernes": "V", "sábado": "S", "sabado": "S", "domingo": "G"}

MONTHS = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
          "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11,
          "diciembre": 12}

TIME_NOUNS = {"semana", "mes", "año", "día", "noche", "tarde", "mañana", "madrugada", "década",
              "siglo", "hora", "minuto", "temporada", "jornada", "trimestre", "semestre", "época",
              "verano", "invierno", "otoño", "primavera", "fin_de_semana", "víspera", "mediodía"}

DEGREE_ADVERBS = {"muy", "más", "menos", "tan", "tanto", "bastante", "demasiado", "poco", "mucho",
                  "algo", "casi", "sumamente", "realmente", "totalmente", "completamente", "bien",
                  "nada", "super", "medio", "extremadamente", "altamente", "particularmente"}

# verb + infinitive / gerund periphrases that FreeLing groups inside a single verb_ chunk
# lemma -> (required linking word or None, required verb form of the dependent)
PERIPHRASES = {"poder": (None, "Inf"), "deber": (None, "Inf"), "soler": (None, "Inf"),
               "tener": ("que", "Inf"), "haber": ("que", "Inf"), "ir": ("a", "Inf"),
               "volver": ("a", "Inf"), "acabar": ("de", "Inf"), "dejar": ("de", "Inf"),
               "empezar": ("a", "Inf"), "comenzar": ("a", "Inf"), "estar": (None, "Ger"),
               "seguir": (None, "Ger")}

SUBORDINATORS = {"que", "si", "como", "cuando", "donde"}

SENTENCE_FINAL = {".", "?", "!", "...", "…"}
QUOTE_PAIRS = {'"': '"', "«": "»", "“": "”"}

CLAUSE_LEVEL_DEPS = {"nsubj", "nsubj:pass", "csubj", "csubj:pass", "aux", "aux:pass", "cop", "mark",
                     "advcl", "obl", "obl:arg", "obl:agent", "obl:tmod", "iobj", "obj", "expl",
                     "expl:pass", "expl:impers", "expl:pv", "parataxis", "discourse", "vocative",
                     "dislocated", "ccomp", "xcomp", "cc", "dep"}

NOMINAL_POS = {"NOUN", "PROPN", "PRON", "NUM", "X", "SYM"}


# --------------------------------------------------------------------------------------------------
# Words
# --------------------------------------------------------------------------------------------------

class Word(object):
    def __init__(self, form, lemma, pos, dep, feats, ent_type=""):
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.dep = dep
        self.feats = feats
        self.ent_type = ent_type
        self.head = None
        self.i = 0
        self.semantic_class = None
        self.is_date = False
        self.date_lemma = None
        self.merged = False
        self.relative_role = False
        self.tag = None
        self.token_indexes = []

    def lower(self):
        return self.form.lower()

    def verb_form(self):
        return eagles._first(self.feats.get("VerbForm"))

    def is_verbal(self):
        return self.pos in ("VERB", "AUX")

    def __repr__(self):
        return "%s/%s/%s" % (self.form, self.pos, self.dep)


def token_features(token):
    return dict(token.morph.to_dict())


def words_from_doc(doc):
    words = []
    by_token = {}
    for token in doc:
        if token.text.strip() == "" or token.pos_ == "SPACE":
            continue
        word = Word(token.text, token.lemma_, token.pos_, token.dep_.lower() if token.dep_ else "dep",
                    token_features(token), token.ent_type_)
        word.token_indexes = [token.i]
        by_token[token.i] = word
        words.append(word)

    roots = []
    for token in doc:
        if token.i not in by_token:
            continue
        word = by_token[token.i]
        head = token.head
        while head.i not in by_token and head.head.i != head.i:
            head = head.head
        if head.i == token.i or head.i not in by_token:
            roots.append(word)
        else:
            word.head = by_token[head.i]

    # spaCy may split a sentence in two; the FreeLing tree has a single root
    for extra_root in roots[1:]:
        extra_root.head = roots[0]
        extra_root.dep = "parataxis"
    if roots:
        roots[0].dep = "root"

    renumber(words)
    return words


def renumber(words):
    for index, word in enumerate(words):
        word.i = index


def children(words, head):
    return [word for word in words if word.head is head]


def dominates(head, word):
    node = word
    while node is not None:
        if node is head:
            return True
        node = node.head
    return False


def subtree(words, head):
    return [word for word in words if dominates(head, word)]


def merge(words, span, pos=None, lemma=None, joiner="_"):
    """Replaces the contiguous words in span by a single multiword (FreeLing style: Buenos_Aires)."""
    span = sorted(span, key=lambda w: w.i)
    span_set = set(span)
    roots = [w for w in span if w.head not in span_set]
    root = roots[0]

    word = Word(joiner.join(w.form for w in span),
                lemma if lemma is not None else joiner.join((w.lemma or w.form).lower() for w in span),
                pos or root.pos, root.dep, dict(root.feats), root.ent_type)
    word.head = root.head
    word.merged = True
    word.token_indexes = sum((w.token_indexes for w in span), [])
    for other in words:
        if other not in span_set and other.head in span_set:
            other.head = word

    position = words.index(span[0])
    words[position:position + len(span)] = [word]
    renumber(words)
    return word


# --------------------------------------------------------------------------------------------------
# Preprocessing (multiwords, dates, contractions, periphrases, projectivity)
# --------------------------------------------------------------------------------------------------

def feats_from_tag(tag):
    """Gender / Number / VerbForm of an EAGLES tag, in UD terms."""
    gender = number = None
    feats = {}
    category = tag[0]
    if category in "NADP" and len(tag) > 4:
        gender, number = (tag[2], tag[3]) if category == "N" else (tag[3], tag[4])
    elif category == "V" and len(tag) > 6:
        feats["VerbForm"] = {"N": "Inf", "G": "Ger", "P": "Part"}.get(tag[2], "Fin")
        gender, number = (tag[6], tag[5]) if tag[2] == "P" else (None, tag[5])
    if gender in ("M", "F"):
        feats["Gender"] = "Masc" if gender == "M" else "Fem"
    if number in ("S", "P"):
        feats["Number"] = "Sing" if number == "S" else "Plur"
    return feats


def apply_lexicon(words, lexicon):
    """Fixes spaCy's closed class mistakes and lemmas with the FreeLing dictionary."""
    for word in words:
        lower = word.lower()
        if re.match(r"^\d+([.,]\d+)*$", word.form) and word.pos in ("NOUN", "PROPN", "X", "ADJ"):
            word.pos = "NUM"
        # spaCy sometimes tags quotes as proper nouns ("«Hola»"), which would merge them with the words
        if word.pos != "PUNCT" and all(unicodedata.category(char).startswith("P") for char in word.form):
            word.pos = "PUNCT"
        # a determiner depending on a verb is a clitic: "lo vio", "Comiendo los" (but not "lo dicho")
        verbal_head = word.head is not None and word.head.is_verbal()
        clitic_role = word.dep in ("obj", "iobj", "expl", "expl:pv", "expl:pass", "expl:impers") \
            or (verbal_head and word.i > word.head.i)
        if lower in CLITIC_PRONOUNS and word.pos == "DET" and verbal_head and clitic_role \
                and not children(words, word):
            word.pos = "PRON"
            word.feats = dict(word.feats, PronType="Prs")
        elif lower == "lo" and word.pos == "PRON" and word.dep == "det":
            word.pos = "DET"
            word.feats = {"Definite": "Def", "PronType": "Art"}
        elif word.dep == "mark" and word.pos in ("PRON", "ADV") and lower in SUBORDINATORS:
            # a subordinator is a conjunction (CS); a relative pronoun tag there makes the model look for an
            # antecedent of a clause that has none
            word.pos = "SCONJ"
            word.feats = {}
        analyses = lexicon.analyses(word.form)
        if word.dep in ("cop", "aux", "aux:pass") and not word.is_verbal():
            verbal = [tag for _, tag in analyses if tag.startswith("V")]
            if verbal:
                word.pos = "AUX"
                word.feats = dict(word.feats)
                word.feats.update(feats_from_tag(verbal[0]))
        if word.pos == "PROPN" and word.form[:1].islower() and analyses:
            # spaCy sometimes takes common words for proper nouns ("El perro come."): a lowercase word
            # the dictionary knows gets its category from it (a verb if it heads a clause)
            heads_clause = word.dep == "root" or any(c.dep in ("nsubj", "obj", "iobj", "obl", "aux", "cop")
                                                     for c in children(words, word))
            for prefix in (("V", "N", "A", "R") if heads_clause else ("N", "A", "V", "R")):
                candidates = [tag for _, tag in analyses if tag.startswith(prefix)]
                if candidates:
                    word.pos = eagles.pos_for_tag(candidates[0])
                    word.feats = dict(word.feats)
                    word.feats.update(feats_from_tag(candidates[0]))
                    break
        corrected = eagles.closed_class_correction(word, analyses)
        if corrected:
            word.pos = corrected
        choice = eagles.choose_analysis(word, analyses)
        if choice:
            word.lemma = choice[0]
    return words


def _lemma_candidates(word, lexicon):
    return set([(word.lemma or "").lower()] + [lemma for lemma, _ in lexicon.analyses(word.form)])


def merge_locutions(words, lexicon):
    """FreeLing multiwords (resources/locucions_extended.dat): lo_cual, pese_a, a_pesar_de..."""
    def matches(component, word):
        kind, value = component
        if kind == "form":
            return word.lower() == value
        return value in _lemma_candidates(word, lexicon)

    def resolve_tag(spec, span):
        if not spec.startswith("$"):
            return spec if valid_tag(spec) else None
        position, prefix = spec[1:].split(":", 1)
        word = span[int(position) - 1]
        candidates = [tag for _, tag in lexicon.analyses(word.form) if tag.startswith(prefix)]
        generated = eagles.tag_of(word)
        if candidates:
            return max(candidates, key=lambda tag: eagles._similarity(tag, generated))
        return generated if generated.startswith(prefix) else None

    index = 0
    while index < len(words):
        word = words[index]
        best = None
        if not (word.merged or word.is_date or word.pos == "PUNCT"):
            candidates = lexicon.locutions_starting_with(word.form, _lemma_candidates(word, lexicon))
            for components, lemma, spec in candidates:
                span = words[index:index + len(components)]
                if len(span) != len(components) or any(w.merged or w.is_date or w.pos == "PUNCT" for w in span):
                    continue
                if not all(matches(c, w) for c, w in zip(components, span)):
                    continue
                tag = resolve_tag(spec, span)
                if tag and (best is None or len(span) > len(best[0])):
                    best = (span, lemma, tag)
        if best:
            span, lemma, tag = best
            merged = merge(words, span, pos=eagles.pos_for_tag(tag), lemma=lemma.lower())
            merged.tag = tag
            merged.feats.update(feats_from_tag(tag))
            if tag.startswith("PR"):
                merged.feats["PronType"] = "Rel"
        index += 1
    return words


def _is_day(form):
    return form.isdigit() and 1 <= int(form) <= 31


def _is_year(form):
    return form.isdigit() and len(form) == 4


def merge_dates(words):
    """Dates become a single W word whose lemma is FreeLing's [day_of_week:day/month/year:hh.mm:period]."""
    index = 0
    while index < len(words):
        forms = [w.form.lower() for w in words]
        match = _date_at(words, forms, index)
        if not match:
            index += 1
            continue
        length, day_of_week, day, month, year = match
        lemma = "[%s:%s/%s/%s:??.??:??]" % (day_of_week or "??", day or "??", month or "??", year or "??")
        span = words[index:index + length]
        word = merge(words, span, pos="NOUN", lemma=lemma) if length > 1 else span[0]
        word.is_date = True
        word.date_lemma = lemma
        word.lemma = lemma
        index += 1
    return words


def _date_at(words, forms, index):
    def at(position):
        return forms[position] if position < len(forms) else None

    position = index
    day_of_week = None
    if at(position) in DAYS_OF_WEEK:
        day_of_week = DAYS_OF_WEEK[at(position)]
        position += 1
        if at(position) == "," and at(position + 1) and _is_day(at(position + 1)):
            position += 1

    numeric = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", at(position) or "")
    if numeric:
        return position + 1 - index, day_of_week, numeric.group(1), numeric.group(2), numeric.group(3)

    if at(position) and _is_day(at(position)) and at(position + 1) == "de" and at(position + 2) in MONTHS:
        day, month = at(position), MONTHS[at(position + 2)]
        position += 3
        year = None
        if at(position) in ("de", "del") and at(position + 1) and _is_year(at(position + 1)):
            year = at(position + 1)
            position += 2
        return position - index, day_of_week, day, month, year

    if day_of_week is not None:
        return position - index, day_of_week, None, None, None

    if at(position) in MONTHS and words[position].form.islower():
        month = MONTHS[at(position)]
        position += 1
        year = None
        if at(position) in ("de", "del") and at(position + 1) and _is_year(at(position + 1)):
            year = at(position + 1)
            position += 2
        return position - index, None, None, month, year

    return None


def merge_named_entities(words, doc):
    by_token = {}
    for word in words:
        for token_index in word.token_indexes:
            by_token[token_index] = word

    for ent in doc.ents:
        span = []
        for token_index in range(ent.start, ent.end):
            word = by_token.get(token_index)
            if word is not None and word in words and word not in span:
                span.append(word)
        span = sorted(span, key=lambda w: w.i)
        while span and span[0].pos in ("DET", "ADP", "PUNCT", "CCONJ"):
            span = span[1:]
        while span and span[-1].pos in ("DET", "ADP", "PUNCT", "CCONJ"):
            span = span[:-1]
        if not span or any(w.is_date for w in span):
            continue
        if span[-1].i - span[0].i + 1 != len(span):
            continue
        capitalized = lambda w: w.form[:1].isupper()
        if not (capitalized(span[0]) and capitalized(span[-1])):
            continue
        if not all(w.pos in ("PROPN", "NOUN", "ADJ", "NUM", "X") and capitalized(w) or w.pos in ("ADP", "DET")
                   for w in span):
            continue

        semantic_class = SEMANTIC_CLASS_BY_ENT.get(ent.label_, "V0")
        if len(span) == 1:
            if span[0].pos in ("PROPN", "X") or (span[0].pos == "NOUN" and span[0].i > 0):
                span[0].pos = "PROPN"
                span[0].semantic_class = semantic_class
            continue
        word = merge(words, span, pos="PROPN")
        word.semantic_class = semantic_class

    # proper noun sequences spaCy did not recognize as an entity (Fulano Mengano)
    index = 0
    while index < len(words) - 1:
        word, following = words[index], words[index + 1]
        if word.pos == "PROPN" and following.pos == "PROPN" and not word.is_date and not following.is_date \
                and (following.head is word or word.head is following) \
                and (following.dep in ("flat", "compound", "appos") or word.dep in ("flat", "compound")):
            semantic_class = word.semantic_class or following.semantic_class
            merged = merge(words, [word, following], pos="PROPN")
            merged.semantic_class = semantic_class
            continue
        index += 1
    return words


def merge_compound_conjunctions(words):
    """para que, sin que, hasta que... (two 'mark' words of the same verb) -> para_que (CS)."""
    for word in list(words):
        if word not in words:
            continue
        marks = sorted([c for c in children(words, word) if c.dep == "mark"], key=lambda w: w.i)
        for first, second in zip(marks, marks[1:]):
            if second.i == first.i + 1 and second.lower() == "que" and first.pos in ("ADP", "ADV", "SCONJ"):
                merged = merge(words, [first, second], pos="SCONJ")
                merged.dep = "mark"
                break
    return words


def split_contractions(words):
    """del -> de + el, al -> a + el (FreeLing splits the contraction; the model expects the article)."""
    index = 0
    while index < len(words):
        word = words[index]
        if word.pos in ("ADP", "DET") and word.lower() in ("del", "al") and not word.merged:
            if word.pos == "DET":
                word.pos, word.dep = "ADP", "case"
            word.form = word.form[:-1]
            word.lemma = word.lower()
            article = Word("el", "el", "DET", "det",
                           {"Definite": "Def", "Gender": "Masc", "Number": "Sing", "PronType": "Art"})
            article.head = word.head if word.head is not None else word
            article.token_indexes = list(word.token_indexes)
            words.insert(index + 1, article)
            renumber(words)
            index += 1
        index += 1
    return words


def normalize_periphrases(words):
    """'puede comprar' annotated as xcomp(puede, comprar) -> aux(comprar, puede), as FreeLing groups it."""
    for head in list(words):
        if head.lemma not in PERIPHRASES or not head.is_verbal():
            continue
        linker, verb_form = PERIPHRASES[head.lemma]
        candidates = [c for c in children(words, head) if c.dep == "xcomp" and c.i > head.i
                      and c.pos == "VERB" and c.verb_form() == verb_form]
        if not candidates:
            continue
        verb = candidates[0]
        between = words[head.i + 1:verb.i]
        if linker is None and between:
            continue
        if linker is not None and [w.lower() for w in between] != [linker]:
            continue

        verb.head, verb.dep = head.head, head.dep
        for other in words:
            if other.head is head and other is not verb:
                other.head = verb
        head.head, head.dep = verb, "aux"
        for w in between:
            w.head, w.dep = verb, "mark"
    return words


def is_finite_clause(words, word):
    if word.is_verbal() and word.verb_form() not in ("Inf", "Ger", "Part"):
        return True
    return any(c.dep in ("cop", "aux", "aux:pass") and c.verb_form() not in ("Inf", "Ger", "Part")
               for c in children(words, word))


def reroot_nonfinite_root(words):
    """'Caminar por el bosque es peligroso' parsed with 'caminar' as root: the finite clause becomes the
    root and the infinitive its subject, as in FreeLing (grup-verb_[ grup-verb-inf_[...] verb_[es] ...])."""
    root = next((w for w in words if w.head is None), None)
    if root is None or not root.is_verbal() or root.verb_form() != "Inf" or is_finite_clause(words, root):
        return words
    candidates = [c for c in children(words, root) if c.i > root.i and is_finite_clause(words, c)
                  and c.dep in ("ccomp", "parataxis", "advcl", "conj", "xcomp", "acl", "dep", "obj")]
    if not candidates:
        return words
    new_root = candidates[0]
    start = min(w.i for w in subtree(words, new_root))
    for other in children(words, root):
        if other is not new_root and other.i > start:
            other.head = new_root
    new_root.head, new_root.dep = None, "root"
    root.head, root.dep = new_root, "csubj"
    return words


def reroot_subordinate_root(words):
    """'Mientras el mundo veía..., otro dispositivo estaba siendo enterrado' parsed with the subordinate
    clause as root: the main clause (no subordinator) becomes the root, as FreeLing has it."""
    root = next((w for w in words if w.head is None), None)
    if root is None or not any(c.dep == "mark" and c.i < root.i for c in children(words, root)):
        return words
    candidates = [c for c in children(words, root)
                  if c.i > root.i and c.dep in ("advcl", "parataxis", "conj", "ccomp")
                  and is_finite_clause(words, c) and not any(m.dep == "mark" for m in children(words, c))]
    if not candidates:
        return words
    new_root = candidates[0]
    start = min(w.i for w in subtree(words, new_root))
    for other in children(words, root):
        if other is not new_root and other.i > start:
            other.head = new_root
    new_root.head, new_root.dep = None, "root"
    root.head, root.dep = new_root, "advcl"
    return words


def split_discontinuous_auxiliaries(words):
    """'puede un hombre cambiar': the verb_ chunk cannot hold 'puede' and 'cambiar' with the subject in
    between, so the auxiliary becomes the clause head and the infinitive its complement (grup-verb-inf)."""
    for verb in list(words):
        if verb.pos != "VERB":
            continue
        auxiliaries = sorted([c for c in children(words, verb) if c.dep in ("aux", "aux:pass")
                              and c.is_verbal() and c.i < verb.i], key=lambda w: w.i)
        if not auxiliaries:
            continue
        allowed = set(auxiliaries)
        allowed.update(c for c in children(words, verb) if c.dep in ("mark", "advmod")
                       and c.pos in ("ADP", "SCONJ", "ADV") and not children(words, c))
        gap = [w for w in words[auxiliaries[0].i + 1:verb.i] if w not in allowed]
        if not gap:
            continue
        before_gap = [a for a in auxiliaries if a.i < gap[0].i]
        if not before_gap:
            continue
        new_head = before_gap[-1]
        new_head.head, new_head.dep = verb.head, verb.dep
        last_gap = gap[-1].i
        for other in children(words, verb):
            stays = other.i > last_gap and other in allowed
            if other is not new_head and other.i < verb.i and not stays:
                other.head = new_head
        verb.head, verb.dep = new_head, "xcomp"
    return words


def projectivize(words):
    """Lifts dependents until every arc is projective, so every phrase covers a contiguous span."""
    changed = True
    guard = 0
    while changed and guard < 10 * len(words) + 10:
        changed = False
        guard += 1
        for word in words:
            head = word.head
            if head is None:
                continue
            low, high = min(word.i, head.i), max(word.i, head.i)
            if any(not dominates(head, words[k]) for k in range(low + 1, high)):
                word.head = head.head if head.head is not None else head
                if word.head is head:
                    continue
                changed = True
                break
    return words


def attach_quotes(words):
    """Quotes go next to the quoted constituent (not inside it), as in FreeLing trees where the
    F-no-c quote nodes are siblings of the cited text. textualCite and quoteFinder rely on that."""
    stack = []
    pairs = []
    for word in words:
        if word.form in QUOTE_PAIRS and not (word.form == '"' and stack and stack[-1].form == '"'):
            if word.form in ("”", "»"):
                continue
            stack.append(word)
        elif stack and word.form == QUOTE_PAIRS[stack[-1].form]:
            pairs.append((stack.pop(), word))

    for opening, closing in pairs:
        region = words[opening.i + 1:closing.i]
        if not region:
            continue
        region_set = set(region)
        heads = [w for w in region if w.head not in region_set]
        governors = set(w.head for w in heads)
        if len(governors) != 1:
            continue
        governor = governors.pop()
        if governor is None or governor in (opening, closing):
            continue
        for quote in (opening, closing):
            quote.head = governor
            quote.dep = "punct"
            for other in words:
                if other.head is quote:
                    other.head = governor
    projectivize(words)
    return words


def is_relative_clause(word):
    """acl clauses, and clauses coordinated with one ("que intentó llevar... y que fue cancelado")."""
    while word is not None:
        if (word.dep or "").startswith("acl"):
            return True
        if word.dep != "conj":
            return False
        word = word.head
        while word is not None and word.dep in ("xcomp", "aux", "aux:pass", "cop"):
            word = word.head
    return False


def mark_relative_pronouns(words):
    for word in words:
        if eagles.is_relative(word) and word.pos in ("PRON", "ADV", "DET"):
            clause = word
            while clause is not None and not is_relative_clause(clause):
                if clause.is_verbal() and clause.dep not in ("aux", "aux:pass", "cop"):
                    break
                clause = clause.head
            if clause is not None and is_relative_clause(clause):
                word.relative_role = True


def preprocess(doc):
    words = words_from_doc(doc)
    if not words:
        return words
    lexicon = get_lexicon()
    apply_lexicon(words, lexicon)
    merge_dates(words)
    merge_named_entities(words, doc)
    # FreeLing's locutions come in both forms ("al_menos", "en_contra_de" + "el"): before and after splitting
    merge_locutions(words, lexicon)
    split_contractions(words)
    merge_locutions(words, lexicon)
    merge_compound_conjunctions(words)
    normalize_periphrases(words)
    reroot_nonfinite_root(words)
    reroot_subordinate_root(words)
    renumber(words)
    projectivize(words)
    split_discontinuous_auxiliaries(words)
    projectivize(words)
    attach_quotes(words)
    mark_relative_pronouns(words)
    for word in words:
        if word.is_date:
            word.lemma, word.tag = word.date_lemma, "W"
            continue
        if word.tag:
            continue
        choice = eagles.choose_analysis(word, lexicon.analyses(word.form))
        if choice:
            word.lemma, word.tag = choice
        else:
            word.lemma = eagles.lemma_of(word)
            word.tag = eagles.tag_of(word)
        # labels (n-fs, grup-nom-mp...) agree with the tag, as in FreeLing
        for key, value in feats_from_tag(word.tag).items():
            if key != "VerbForm":
                word.feats[key] = value
    return words


# --------------------------------------------------------------------------------------------------
# Tree
# --------------------------------------------------------------------------------------------------

class Leaf(object):
    def __init__(self, word, head=False):
        self.word = word
        self.head = head

    def first(self):
        return self.word.i

    def words(self):
        return [self.word]


class Node(object):
    def __init__(self, label, children=None):
        self.label = label
        self.children = [child for child in (children or []) if child is not None]
        self.head = False

    def first(self):
        return min(child.first() for child in self.children)

    def words(self):
        return sum((child.words() for child in self.children), [])

    def sort(self):
        self.children.sort(key=lambda child: child.first())
        for child in self.children:
            if isinstance(child, Node):
                child.sort()
        return self


def node(label, children, head=None):
    """Builds a label node; `head` is the child (object) marked with '+'."""
    result = Node(label, children)
    if head is not None:
        head.head = True
    elif result.children:
        result.children[0].head = True
    return result


def gn(word, need_gender=True):
    """FreeLing label suffix: gender + number (ms, fp...); without gender only the number (s, p)."""
    gender = {"Masc": "m", "Fem": "f"}.get(eagles._first(word.feats.get("Gender")))
    if word.lower() in eagles.NEUTER_PRONOUNS:
        gender = "m"
    number = "p" if eagles._first(word.feats.get("Number")) == "Plur" else "s"
    if gender is None:
        if not need_gender:
            return number
        gender = "m"
    return gender + number


class TreeBuilder(object):
    def __init__(self, words):
        self.words = words
        self.kids = dict((id(w), sorted(children(words, w), key=lambda c: c.i)) for w in words)
        self.forced_kinds = {}
        last = len(words) - 1
        while last >= 0 and words[last].form in SENTENCE_FINAL | {'"', "»", "”", ")"}:
            last -= 1
        self.final_punctuation = set(w for w in words[last + 1:] if w.form in SENTENCE_FINAL)

    def children_of(self, word):
        return self.kids[id(word)]

    def set_children(self, word, kids):
        self.kids[id(word)] = sorted(kids, key=lambda c: c.i)

    def span_of(self, word):
        """Positions covered by the subtree of word (with the current, possibly modified, children)."""
        positions = [word.i]
        for child in self.children_of(word):
            positions.extend(self.span_of(child))
        return positions

    # ---------------------------------------------------------------------------------- entry point

    def build(self):
        roots = [w for w in self.words if w.head is None]
        root = roots[0]
        quoted = self.initial_quote_tree()
        if quoted is not None:
            return quoted.sort()

        nodes = self.build_dep(root, top=True)
        if len(nodes) == 1 and isinstance(nodes[0], Node):
            return nodes[0].sort()
        # several top level nodes (a subordinate clause and what precedes it...): they hang from the main verb
        # group; a wrapper without a verb of its own would be a clause with an empty proper tree
        main = next((n for n in nodes if isinstance(n, Node) and n.label in ("grup-verb", "verb-pass")
                     and any(isinstance(c, Node) and c.label in ("verb", "parti-flex") for c in n.children)), None)
        if main is not None:
            main.children.extend(n for n in nodes if n is not main)
            return main.sort()
        # no verb group at the top (a fragment): a verbless root, the model reads it as a minor sentence
        return node("sn", nodes).sort()

    # ------------------------------------------------------------------------------------ dispatch

    def kind(self, word):
        if id(word) in self.forced_kinds:
            return self.forced_kinds[id(word)]
        pos = word.pos
        if word.is_date:
            return "nominal"
        if any(c.dep == "cop" or (c.dep in ("aux", "aux:pass") and c.is_verbal()) for c in self.children_of(word)):
            return "clause"
        if pos in ("PUNCT",) or (pos == "SYM" and word.form != "%"):
            return "punct"
        if pos == "VERB":
            if word.verb_form() == "Part" and (word.dep == "amod" or (word.dep.startswith("acl") and not any(
                    c.dep in ("aux", "aux:pass", "nsubj", "nsubj:pass", "mark") for c in self.children_of(word)))):
                return "adj"
            return "clause"
        if pos == "AUX":
            return "clause"
        if pos in NOMINAL_POS:
            return "nominal"
        if pos == "DET":
            return "nominal" if self.children_of(word) else "det"
        if pos == "ADJ":
            if any(c.dep == "det" for c in self.children_of(word)):
                return "nominal"
            return "adj"
        if pos == "ADV":
            return "adv"
        if pos == "ADP":
            return "adp"
        if pos == "CCONJ":
            return "cc"
        if pos == "SCONJ":
            return "sconj"
        if pos == "INTJ":
            return "intj"
        return "nominal"

    def build_dep(self, word, top=False, in_clause=False):
        """Nodes for word and its subtree, as a dependent of a clause (in_clause) or of a phrase."""
        if self.kind(word) == "punct":
            return [self.punctuation(word)] + self.build_children(self.children_of(word), in_clause)
        conjuncts = [c for c in self.children_of(word) if c.dep == "conj"]
        if conjuncts and self.kind(word) == "clause" and not word.is_verbal():
            # only other clauses coordinate with a copulative clause; attributes stay in its predicate
            conjuncts = [c for c in conjuncts if self.kind(c) == "clause"]
        if conjuncts:
            return self.coordination(word, conjuncts, top, in_clause)
        return self.build_single(word, top, in_clause)

    def build_children(self, kids, in_clause=False):
        nodes = []
        for kid in kids:
            nodes.extend(self.build_dep(kid, in_clause=in_clause))
        return nodes

    def build_single(self, word, top=False, in_clause=False):
        kind = self.kind(word)
        if kind == "clause":
            return self.clause(word)
        if kind == "nominal":
            return self.nominal(word, self.children_of(word), in_clause)
        if kind == "adj":
            return self.adjective(word, self.children_of(word), predicative=in_clause or top)
        if kind == "adv":
            return self.adverb(word, self.children_of(word))
        if kind == "punct":
            return [self.punctuation(word)]
        rest = self.build_children(self.children_of(word))
        if kind == "cc":
            return [node("coord", [Leaf(word)])] + rest
        if kind == "sconj":
            return [Leaf(word)] + rest
        if kind == "intj":
            return [node("interjeccio", [Leaf(word)])] + rest
        if kind == "adp":
            return [node("prep", [Leaf(word)])] + rest
        if kind == "det":
            return [self.specifier([word])] + rest
        return [Leaf(word)] + rest

    def punctuation(self, word):
        if word in self.final_punctuation:
            label = "F-term"
        elif word.form == ",":
            label = "Fc"
        else:
            label = "F-no-c"
        return node(label, [Leaf(word)])

    # ---------------------------------------------------------------------------------- coordination

    def coordination(self, word, conjuncts, top, in_clause):
        conjuncts = sorted(conjuncts, key=lambda c: c.i)
        own = [c for c in self.children_of(word) if c not in conjuncts]
        first_start = min(self.span_of(conjuncts[0]))
        before = [c for c in own if c.i < first_start]
        trailing = [c for c in own if c.i > first_start]
        self.set_children(word, before)
        # dependents of the first conjunct placed after the others go to the conjunct that precedes them
        for c in trailing:
            target = [conj for conj in conjuncts if min(self.span_of(conj)) < c.i][-1]
            self.set_children(target, self.children_of(target) + [c])
            c.head = target
        # ...except the punctuation closing the whole coordination, which stays at its level
        last = conjuncts[-1]
        trailing_punct = []
        for c in sorted(trailing, key=lambda w: w.i, reverse=True):
            others = [p for p in self.span_of(last) if p != c.i and p not in [t.i for t in trailing_punct]]
            if self.kind(c) == "punct" and not self.children_of(c) and c.head is last and c.i > max(others):
                trailing_punct.insert(0, c)
            else:
                break
        self.set_children(last, [c for c in self.children_of(last) if c not in trailing_punct])

        kind = self.kind(word)
        parts = self.build_single(word, in_clause=in_clause)
        for conjunct in conjuncts:
            # separators are the leading cc/punct children of the conjunct (", y B")
            separators = []
            for c in self.children_of(conjunct):
                if c.i < conjunct.i and c.dep in ("cc", "punct") and not self.children_of(c):
                    separators.append(c)
                else:
                    break
            self.set_children(conjunct, [c for c in self.children_of(conjunct) if c not in separators])
            for separator in separators:
                if separator.pos == "CCONJ":
                    parts.append(node("coord", [Leaf(separator)]) if kind in ("adj", "adv") else Leaf(separator))
                else:
                    parts.append(self.punctuation(separator))
            parts.extend(self.build_single(conjunct, in_clause=in_clause))

        heads = [p for p in parts if isinstance(p, Leaf) and p.word.pos == "CCONJ"]
        clause_labels = ("grup-verb", "verb-pass", "subord", "subord-rel", "subord-ger")
        if kind == "clause" and all(isinstance(p, Node) and p.label in clause_labels for p in parts):
            # clauses juxtaposed without conjunction or punctuation of their own: a coor-vb holding only
            # clauses would be a clause with nothing in it, so they stay siblings
            return parts + [self.punctuation(p) for p in trailing_punct]
        if kind == "clause":
            label = "coor-vb"
        elif kind == "adj":
            label = "s-a-" + gn(word)
        elif kind == "adv":
            label = "sadv"
        elif all(isinstance(p, Node) and p.label in ("grup-sp", "sp-de")
                 for p in parts if not (isinstance(p, Leaf) or p.label in ("Fc", "F-no-c", "coord"))):
            label = "coor-sp"
        else:
            label = "coor-n"
        result = node(label, parts, heads[0] if heads else None)

        punct_nodes = [self.punctuation(p) for p in trailing_punct]
        if top:
            result.children.extend(punct_nodes)
            return [result]
        return [result] + punct_nodes

    # ---------------------------------------------------------------------------------------- clauses

    def clause(self, predicate):
        kids = self.children_of(predicate)
        # spaCy sometimes hangs the subject or the subordinator on the copula / auxiliary ("todo lo dicho
        # es...", "Si el universo estuviera..."): the verb chunk only holds the verbs, so those dependents
        # go up to the clause
        for kid in list(kids):
            if kid.dep in ("cop", "aux", "aux:pass") and self.children_of(kid):
                for grandchild in self.children_of(kid):
                    grandchild.head = predicate
                self.set_children(predicate, kids + self.children_of(kid))
                self.set_children(kid, [])
                kids = self.children_of(predicate)
        copula = next((c for c in kids if c.dep == "cop"), None)
        if copula is None and not predicate.is_verbal():
            # spaCy may attach ser / estar to an adjective or noun predicate as 'aux' ("han sido malos")
            verbal = [c for c in kids if c.dep in ("aux", "aux:pass") and c.is_verbal() and c.i < predicate.i]
            if verbal:
                copula = verbal[-1]
        if copula is not None and copula.lemma == "ser" and self.make_participle(predicate):
            # ser + participle is FreeLing's verb-pass, even when spaCy reads an adjective ("fue detenido")
            copula.dep = "aux:pass"
            copula = None
        verb = copula or predicate

        auxiliaries = [c for c in kids if c.dep in ("aux", "aux:pass") and c.is_verbal() and c.i < verb.i
                       and c is not copula]
        chunk_start = min([a.i for a in auxiliaries] + [verb.i])
        between = [c for c in kids if chunk_start < c.i < verb.i and c not in auxiliaries
                   and not self.children_of(c) and c.pos in ("ADP", "SCONJ", "ADV", "PART")
                   and c.dep in ("mark", "advmod")]

        relative = self.relative_group(predicate, kids, chunk_start)
        marks = sorted([c for c in kids if c.dep == "mark" and c.i < chunk_start and c not in between],
                       key=lambda w: w.i)
        # only the run of subordinators that opens the clause wraps it ("que el mundo tal y como...")
        leading = marks[:1]
        for m in marks[1:]:
            if m.i == leading[-1].i + 1 and not self.children_of(leading[-1]):
                leading.append(m)
            else:
                break
        marks = leading
        handled = set(auxiliaries + between + marks + ([copula] if copula else []))
        if relative is not None:
            handled.add(relative)

        passive = copula is None and verb.pos == "VERB" and verb.verb_form() == "Part" \
            and any(a.lemma == "ser" for a in auxiliaries)
        first_verb = min(auxiliaries + [verb], key=lambda w: w.i)
        form = first_verb.verb_form() or "Fin"
        # FreeLing never heads a grup-verb with a non finite verb (the model would look for its person and
        # number), not even at the top of the sentence
        nonfinite = form if form in ("Inf", "Ger", "Part") else None

        if copula is not None:
            # the attribute cannot span over the copula: dependents on the other side are clause level
            same_side = lambda c: (c.i < copula.i) == (predicate.i < copula.i)
            internal = [c for c in kids if c not in handled and not self.is_clause_level(c, predicate)
                        and same_side(c)]
            internal_span = set(sum((self.span_of(c) for c in internal), [predicate.i]))
            low, high = min(internal_span), max(internal_span)
            internal += [c for c in kids if c not in handled and c not in internal and c.dep == "punct"
                         and low < c.i < high]
            clause_kids = [c for c in kids if c not in handled and c not in internal]
        else:
            internal = []
            clause_kids = [c for c in kids if c not in handled]

        # whatever precedes the subordinator / relative pronoun (usually a comma) stays outside the wrapper
        markers = marks + (self.subtree_words(relative) if relative is not None else [])
        pre_siblings = []
        wrapper_extra = []
        if markers:
            first_marker = min(m.i for m in markers)
            pre_siblings = [c for c in clause_kids if c.i < first_marker]
            clause_kids = [c for c in clause_kids if c not in pre_siblings]

        if nonfinite == "Ger":
            # subord-ger_[ gerund ... ]: VerbExtractor takes its first leaf as the verb
            verbal = sorted(auxiliaries + between + [verb], key=lambda w: w.i)
            before_gerund = [c for c in clause_kids if c.i < verbal[0].i]
            if markers:
                # cannot leave the wrapper: they go inside it, before subord-ger
                wrapper_extra = before_gerund
            else:
                pre_siblings += before_gerund
            clause_kids = [c for c in clause_kids if c not in before_gerund]
            nodes = [Leaf(w) for w in verbal] + self.build_children(clause_kids, True)
            if copula is not None:
                nodes += self.predicate(predicate, internal)
            core = node("subord-ger", nodes, nodes[0])
        elif nonfinite == "Part" and copula is None:
            verbal = sorted(auxiliaries + between + [verb], key=lambda w: w.i)
            participle = node("parti-" + gn(verb), [Leaf(w) for w in verbal], None)
            core = node("subord-part", [participle] + self.build_children(clause_kids, True), participle)
        else:
            chunk = self.verb_chunk(auxiliaries, between, verb, passive, nonfinite == "Inf")
            nodes = chunk + self.build_children(clause_kids, True)
            if copula is not None:
                nodes += self.predicate(predicate, internal)
            head = next((n for n in chunk if n.label in ("verb", "parti-flex", "infinitiu")), chunk[0])
            if nonfinite == "Inf":
                label = "grup-verb-inf"
            else:
                label = "verb-pass" if passive else "grup-verb"
            core = node(label, nodes, head)

        if relative is not None:
            group = sorted(self.subtree_words(relative), key=lambda w: w.i)
            if len(group) == 1:
                relative_node = Leaf(group[0])
            else:
                relative_node = node("relatiu", [Leaf(w) for w in group])
            extra = self.build_children(wrapper_extra, True)
            if core.label in ("grup-verb", "verb-pass", "subord-ger"):
                wrapped = node("subord-rel", [relative_node] + extra + [core], relative_node)
            else:
                # no verb group for the model to take the voice from: the relative stays inside the clause
                core.children = [relative_node] + extra + core.children
                wrapped = core
        elif marks:
            marks = sorted(marks, key=lambda w: w.i)
            mark_children = []
            for m in marks:
                mark_children.append(Leaf(m))
                mark_children.extend(self.build_children(self.children_of(m)))
            extra = self.build_children(wrapper_extra, True)
            if all(m.pos == "ADP" for m in marks):
                preposition = node("prep", mark_children)
                label = "grup-sp-inf" if core.label == "grup-verb-inf" else "grup-sp"
                wrapped = node(label, [preposition] + extra + [core], preposition)
            elif core.label in ("grup-verb", "verb-pass", "subord-ger"):
                wrapped = node("subord", mark_children + extra + [core], mark_children[0])
            else:
                # "Gracias por llevar...", "aunque cansado": no verb group to take the voice from
                core.children = mark_children + extra + core.children
                wrapped = core
        else:
            wrapped = core

        return self.build_children(pre_siblings, True) + [wrapped]

    def make_participle(self, word):
        """Turns an attribute that has a participle reading in the FreeLing dictionary into the verb."""
        if word.pos == "VERB" and word.verb_form() == "Part":
            return True
        if word.pos not in ("ADJ", "NOUN"):
            return False
        if any(c.dep in ("det", "nummod") for c in self.children_of(word)):
            return False
        participles = [analysis for analysis in get_lexicon().analyses(word.form) if analysis[1].startswith("VMP")]
        if not participles:
            return False
        lemma, tag = max(participles, key=lambda analysis: eagles._similarity(analysis[1], word.tag or ""))
        word.pos, word.lemma, word.tag = "VERB", lemma, tag
        word.feats = dict(word.feats)
        word.feats.update(feats_from_tag(tag))
        return True

    def is_clause_level(self, kid, predicate):
        if kid.dep in CLAUSE_LEVEL_DEPS or kid.dep == "punct":
            return True
        if kid.dep == "advmod":
            degree = kid.lower() in DEGREE_ADVERBS and kid.i < predicate.i and predicate.pos in ("ADJ", "ADV")
            return not degree
        return False

    def relative_group(self, predicate, kids, chunk_start):
        if not is_relative_clause(predicate):
            return None
        for kid in kids:
            if kid.i >= chunk_start:
                break
            # the relative phrase ("que", "en la que", "cuyo padre"), never a clause ("qué hacer después...")
            group = self.subtree_words(kid)
            if any(w.relative_role for w in group) and not any(w.is_verbal() for w in group):
                return kid
        return None

    def subtree_words(self, word):
        result = [word]
        for child in self.children_of(word):
            result.extend(self.subtree_words(child))
        return result

    def verb_chunk(self, auxiliaries, between, verb, passive, infinitive_clause):
        """verb_ / vaux_ / vser_ / parti-flex_ nodes (FreeLing groups) for the verbal words of a clause."""
        sequence = sorted(auxiliaries + between + [verb], key=lambda w: w.i)

        if passive:
            ser = [a for a in auxiliaries if a.lemma == "ser"][-1]
            before_ser = [w for w in sequence if w.i < ser.i]
            after_ser = [w for w in sequence if ser.i < w.i < verb.i]
            nodes = []
            if before_ser:
                nodes.append(node("vaux", [Leaf(w) for w in before_ser]))
            nodes.append(node("parti-ser" if ser.verb_form() == "Part" else "vser", [Leaf(ser)]))
            nodes.extend(node("sadv", [Leaf(w)]) for w in after_ser)
            nodes.append(node("parti-flex", [node("parti-" + gn(verb), [Leaf(verb)])]))
            return nodes

        # active voice copula in a compound tense ("ha sido"): FreeLing leaves "sido" outside verb_
        extra = []
        if verb.lemma == "ser" and verb.verb_form() == "Part" and auxiliaries:
            extra = [node("parti-ser", [Leaf(verb)])]
            sequence = [w for w in sequence if w is not verb]
            verb = sequence[-1]

        finite = []
        rest = list(sequence)
        while rest and (rest[0].verb_form() not in ("Inf", "Ger", "Part") or not rest[0].is_verbal()):
            finite.append(rest.pop(0))

        children_nodes = []
        for word in finite:
            if word.is_verbal() and word.lemma in eagles.AUXILIAR_LEMMAS and word is not verb:
                children_nodes.append(node("vaux", [Leaf(word)]))
            elif word.pos == "ADV":
                children_nodes.append(node("sadv", [Leaf(word)]))
            else:
                children_nodes.append(Leaf(word))

        if rest:
            children_nodes.append(self.nonfinite_group(rest))
        if children_nodes:
            children_nodes[-1].head = True

        if infinitive_clause and not finite:
            return children_nodes + extra
        return [node("verb", children_nodes, children_nodes[-1])] + extra

    def nonfinite_group(self, words):
        first = words[0]
        form = first.verb_form()
        if form == "Inf":
            main = words[-1]
            before = [Leaf(w) for w in words[:-1]]
            if main.verb_form() == "Part":
                # "haber jugado": infaux_[ haber ] +parti_[ jugado ]
                inner = [node("infaux", before), node("parti", [Leaf(main)])]
            else:
                # "comprar", "empezar a disparar"
                inner = before + [node("forma-inf", [Leaf(main)])]
            return node("infinitiu", [node("inf", inner, inner[-1])])
        label = "forma-ger" if form == "Ger" else "parti"
        if len(words) == 1:
            return node(label, [Leaf(first)])
        inner = [Leaf(w) for w in words]
        return node(label, inner, inner[-1])

    def predicate(self, word, kids):
        """Attribute of a copulative clause ('es malo', 'es un hombre', 'es de Madrid')."""
        conjuncts = [c for c in kids if c.dep == "conj"]
        if conjuncts:
            # "es grande y voluminoso": coordinated attributes, not coordinated clauses
            adjectival = word.pos == "ADJ" or (word.pos == "VERB" and word.verb_form() == "Part")
            self.forced_kinds[id(word)] = "adj" if adjectival else ("adv" if word.pos == "ADV" else "nominal")
            self.set_children(word, kids)
            nodes = self.coordination(word, conjuncts, False, False)
            if adjectival:
                return [node("s-adj", nodes)]
            return nodes
        if word.pos == "ADJ" or (word.pos == "VERB" and word.verb_form() == "Part"):
            return self.adjective(word, kids, predicative=True)
        if word.pos == "ADV":
            return self.adverb(word, kids)
        return self.nominal(word, kids, in_clause=False)

    # -------------------------------------------------------------------------------------- nominals

    def nominal(self, word, kids, in_clause=False):
        cases = [c for c in kids if c.dep in ("case", "mark") and c.i < word.i and c.pos in ("ADP", "SCONJ")]
        if not cases:
            return self.noun_phrase(word, kids, in_clause)
        # what precedes the preposition (a comma, "incluso"...) stays outside the prepositional phrase
        outside = [c for c in kids if c.i < min(case.i for case in cases) and c not in cases]
        rest = [c for c in kids if c not in cases and c not in outside]
        inner = self.noun_phrase(word, rest, False)
        prepositions = []
        for case in sorted(cases, key=lambda w: w.i):
            prepositions.append(Leaf(case))
            prepositions.extend(self.build_children(self.children_of(case)))
        outside_nodes = self.build_children(outside, in_clause)
        if len(cases) == 1 and cases[0].lower() == "de" and len(prepositions) == 1:
            return outside_nodes + [node("sp-de", prepositions + inner, prepositions[0])]
        preposition = node("prep", prepositions)
        return outside_nodes + [node("grup-sp", [preposition] + inner, preposition)]

    def noun_phrase(self, word, kids, in_clause):
        lower = word.lower()
        # a comma opening the phrase belongs to the enclosing level (", otro dispositivo...")
        content = [word] + [c for c in kids if c.dep != "punct"]
        leading = [c for c in kids if c.dep == "punct" and not self.children_of(c)
                   and c.i < min(w.i for w in content)]
        if leading:
            rest = [c for c in kids if c not in leading]
            return [self.punctuation(c) for c in leading] + self.noun_phrase(word, rest, in_clause)

        if word.pos == "PRON" and lower in CLITIC_PRONOUNS and word.head is not None \
                and word.head.is_verbal() and not kids:
            if lower == "se":
                return [node("morfema-verbal", [Leaf(word)])]
            return [node("patons", [node("paton-" + gn(word, need_gender=False), [Leaf(word)])])]

        is_determiner = lambda c: c.dep in ("det", "predet") and c.pos == "DET" and c.feats.get("NumType") != "Card"
        determiners = []
        for c in kids:
            # "todo lo dicho": spaCy may chain determiners (todo <- lo); FreeLing groups them in one espec
            if c.i < word.i and is_determiner(c) and all(is_determiner(g) and not self.children_of(g)
                                                         for g in self.children_of(c)):
                determiners.append(c)
                determiners.extend(self.children_of(c))
        numbers = [c for c in kids if c.dep in ("nummod", "det") and c.i < word.i and c not in determiners]
        last_specifier = max([c.i for c in determiners + numbers] + [-1])
        pre_modifiers = [c for c in kids if c.dep == "amod" and last_specifier < c.i < word.i]

        post = sorted([c for c in kids if c.i > word.i], key=lambda c: c.i)
        in_nominal_group = []
        for c in post:
            adjectival = c.dep in ("amod", "compound", "flat") or (c.dep.startswith("acl") and self.kind(c) == "adj")
            if not adjectival:
                break
            in_nominal_group.append(c)
        others = [c for c in kids if c not in determiners + numbers + pre_modifiers + in_nominal_group]

        nodes = []
        if determiners:
            if len(determiners) == 1 and determiners[0].lower() == "lo":
                nodes.append(node("j-ms", [Leaf(determiners[0])]))
            else:
                nodes.append(self.specifier(determiners))
        for number in numbers:
            nodes.append(node("numero-nopart", [Leaf(number)] + self.build_children(self.children_of(number))))

        head_node = self.nominal_head(word)
        if word.pos in ("NOUN", "PROPN", "X") and not word.is_date:
            group_children = self.build_children(pre_modifiers) + [head_node] + self.build_children(in_nominal_group)
            group = node("grup-nom-" + self.nominal_gn(word, determiners), group_children, head_node)
            nodes.append(group)
            head = group
        else:
            nodes.extend([head_node] + self.build_children(pre_modifiers + in_nominal_group))
            head = head_node
        nodes.extend(self.build_children(others))

        if word.is_date:
            # dates are time references (DateTimeFinder, FactTimeUtils), never entities: no sn around them
            return [node("data", nodes, head)]
        if in_clause and lower in TIME_NOUNS:
            return [node("sadv", [node("sn-tmp", nodes, head)])]
        return [node("sn", nodes, head)]

    def nominal_gn(self, word, determiners):
        if eagles._first(word.feats.get("Gender")) in ("Masc", "Fem") or not determiners:
            return gn(word)
        number = "p" if eagles._first(word.feats.get("Number")) == "Plur" else "s"
        det_gender = {"Masc": "m", "Fem": "f"}.get(eagles._first(determiners[-1].feats.get("Gender")), "m")
        return det_gender + number

    def nominal_head(self, word):
        if word.is_date:
            return Leaf(word)
        if word.pos == "NUM" or (word.pos == "DET" and word.feats.get("NumType") == "Card"):
            return node("numero", [Leaf(word)])
        if word.pos == "PROPN" or (word.pos == "X" and word.form[:1].isupper()):
            return node("w-" + gn(word), [Leaf(word)])
        if word.pos == "PRON":
            return self.pronoun(word)
        if word.pos == "DET":
            return node(self.determiner_label(word) + "-" + gn(word), [Leaf(word)])
        if word.pos == "ADJ":
            return node("s-a-" + gn(word), [node("a-" + gn(word), [Leaf(word)])])
        return node("n-" + gn(word), [Leaf(word)])

    def pronoun(self, word):
        pron_type = eagles._first(word.feats.get("PronType"))
        if word.relative_role:
            kind = "pindef"
        else:
            kind = {"Prs": "psubj", "Dem": "pdem", "Ind": "pindef", "Tot": "pindef", "Neg": "pindef",
                    "Int": "pinterrog"}.get(pron_type, "psubj" if word.lower() in eagles.PERSONAL_PRONOUN_LEMMAS
                                            else "pindef")
        gender_number = gn(word, need_gender=False)
        has_gender = len(gender_number) == 2
        inner = node(kind + "-" + gender_number, [Leaf(word)])
        return node("pron-" + gender_number if has_gender else "pron", [inner])

    def determiner_label(self, word):
        if word.tag and word.tag.startswith("D"):
            return {"A": "j", "I": "indef", "D": "dem", "P": "pos", "T": "interrog", "E": "interrog"}[word.tag[1]]
        pron_type = eagles._first(word.feats.get("PronType"))
        if word.feats.get("Poss") == "Yes":
            return "pos"
        return {"Art": "j", "Dem": "dem", "Int": "interrog", "Exc": "interrog"}.get(pron_type, "indef")

    def specifier(self, determiners):
        determiners = sorted(determiners, key=lambda w: w.i)
        parts = [node(self.determiner_label(d) + "-" + gn(d), [Leaf(d)]) for d in determiners]
        label_gn = gn(determiners[0])
        if len(parts) == 1:
            return node("espec-" + label_gn, parts)
        return node("espec-" + label_gn, [node("grup-complex-spec-" + label_gn, parts)])

    # ----------------------------------------------------------------------- adjectives and adverbs

    def adjective(self, word, kids, predicative=False):
        degree = [c for c in kids if c.dep == "advmod" and c.i < word.i and c.lower() in DEGREE_ADVERBS
                  and not self.children_of(c)]
        cases = [c for c in kids if c.dep == "case" and c.i < word.i]
        rest = [c for c in kids if c not in degree and c not in cases]
        label = ("parti-" if word.pos == "VERB" or word.feats.get("VerbForm") == "Part" else "a-") + gn(word)
        core = node(label, [Leaf(word)])
        phrase = node("s-a-" + gn(word),
                      [node("cuantif", [Leaf(d)]) for d in degree] + [core] + self.build_children(rest), core)
        if cases:
            preposition = node("prep", [Leaf(c) for c in sorted(cases, key=lambda w: w.i)])
            return [node("grup-sp", [preposition, phrase], preposition)]
        if predicative:
            return [node("s-adj", [phrase])]
        return [phrase]

    def adverb(self, word, kids):
        if word.lower() == "no" and not kids:
            return [node("neg", [Leaf(word)])]
        degree = [c for c in kids if c.dep == "advmod" and c.i < word.i and c.lower() in DEGREE_ADVERBS
                  and not self.children_of(c)]
        cases = [c for c in kids if c.dep in ("case", "mark") and c.i < word.i and c.pos in ("ADP", "SCONJ")]
        rest = [c for c in kids if c not in degree and c not in cases]
        if degree:
            core = node("sadv", [Leaf(word)])
            phrase = node("sadv", [node("cuantif", [Leaf(d)]) for d in degree] + [core]
                          + self.build_children(rest), core)
        else:
            leaf = Leaf(word)
            phrase = node("sadv", [leaf] + self.build_children(rest), leaf)
        if cases:
            preposition = node("prep", [Leaf(c) for c in sorted(cases, key=lambda w: w.i)])
            return [node("grup-sp", [preposition, phrase], preposition)]
        return [phrase]

    # -------------------------------------------------------------------------- quoted sentences

    def initial_quote_tree(self):
        """'"Vamos a ganar", afirmó el ministro.' -> FreeLing leaves this sentence unparsed at the top:
        an F-no-c root whose children are the quote, the cited chunks, the quote, the comma and the
        reporting clause. textualCite / quoteFinder expect exactly that shape."""
        words = self.words
        if len(words) < 4 or words[0].form != '"':
            return None
        closing = next((w for w in words[1:] if w.form == '"'), None)
        if closing is None or closing.i + 2 >= len(words) or words[closing.i + 1].form != ",":
            return None
        cited = words[1:closing.i]
        reporting = words[closing.i + 2:]
        if not cited or not any(w.is_verbal() for w in reporting):
            return None

        nodes = [node("F-no-c", [Leaf(words[0])])]
        nodes += self.region(cited)
        nodes += [node("F-no-c", [Leaf(closing)]), node("Fc", [Leaf(words[closing.i + 1])])]
        nodes += self.region(reporting)
        return node("F-no-c", nodes, nodes[0])

    def region(self, region_words):
        region = set(region_words)
        for w in region_words:
            self.set_children(w, [c for c in self.children_of(w) if c in region])
        roots = [w for w in region_words if w.head not in region]
        nodes = []
        for root in roots:
            nodes.extend(self.build_dep(root, top=root.is_verbal() or self.kind(root) == "clause"))
        return nodes


# --------------------------------------------------------------------------------------------------
# Fallback and serialization
# --------------------------------------------------------------------------------------------------

def flat_tree(words):
    """Used only if the structured tree could not be built in text order: one chunk per word."""
    builder = TreeBuilder(words)
    nodes = []
    for word in words:
        kind = builder.kind(word)
        if kind == "punct":
            nodes.append(builder.punctuation(word))
        elif word.is_verbal():
            nodes.append(node("verb", [Leaf(word)]))
        elif word.is_date:
            nodes.append(node("data", [Leaf(word)]))
        elif kind == "nominal":
            nodes.append(node("sn", [builder.nominal_head(word)]))
        elif kind == "adj":
            nodes.append(node("s-a-" + gn(word), [node("a-" + gn(word), [Leaf(word)])]))
        elif kind == "adv":
            nodes.append(node("sadv", [Leaf(word)]))
        elif kind == "adp":
            nodes.append(node("prep", [Leaf(word)]))
        elif kind == "det":
            nodes.append(builder.specifier([word]))
        else:
            nodes.append(Leaf(word))
    has_verb = any(isinstance(n, Node) and n.label == "verb" for n in nodes)
    return node("grup-verb" if has_verb else "sn", nodes,
                next((n for n in nodes if isinstance(n, Node) and n.label == "verb"), None))


def _contiguous(item):
    positions = [word.i for word in item.words()]
    return positions == list(range(min(positions), min(positions) + len(positions)))


def repair(tree):
    """Dissolves (into their parent) the nodes whose words are not contiguous, which can only come from
    unusual spaCy analyses; the rest of the structure is kept."""
    changed = True
    while changed:
        changed = False
        children_nodes = []
        for child in tree.children:
            if isinstance(child, Node) and not _contiguous(child):
                children_nodes.extend(child.children)
                changed = True
            else:
                children_nodes.append(child)
        tree.children = sorted(children_nodes, key=lambda child: child.first())
    for child in tree.children:
        if isinstance(child, Node):
            repair(child)
    return tree


def build_tree(words):
    try:
        tree = repair(TreeBuilder(words).build())
        if tree.words() == words:
            return tree
    except Exception:
        pass
    return flat_tree(words)


def _clean(text):
    text = re.sub(r"\s+", "_", text.strip())
    return text or "_"


def serialize(tree):
    lines = []

    def emit(item, depth):
        indent = "  " * depth
        mark = "+" if item.head else ""
        if isinstance(item, Leaf):
            word = item.word
            lines.append("%s%s(%s %s %s -)" % (indent, mark, _clean(word.form), _clean(word.lemma),
                                                word.tag or eagles.tag_of(word)))
            return
        lines.append("%s%s%s_[" % (indent, mark, item.label))
        for child in item.children:
            emit(child, depth + 1)
        lines.append("%s]" % indent)

    emit(tree, 0)
    return lines + ["", ""]


def parse_lines(doc):
    """FreeLing analyzer_client compatible output (list of lines) for a spaCy Doc."""
    words = preprocess(doc)
    if not words:
        return ["", ""]
    return serialize(build_tree(words))
