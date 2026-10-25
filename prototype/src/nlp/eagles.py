# -*- coding: utf-8 -*-
"""Universal Dependencies (spaCy) -> FreeLing EAGLES tags and lemmas.

Every tag produced here must be accepted by src.ling.msi_mapper.tag_to_full_msi, which raises on
unknown letters, so each position only takes values listed in src.ling.msi_data.
"""
PUNCTUATION_TAGS = {
    ".": "Fp", ",": "Fc", ":": "Fd", ";": "Fx", '"': "Fe", "'": "Fe", "`": "Fe",
    "-": "Fg", "–": "Fg", "—": "Fg", "/": "Fh", "¿": "Fia", "?": "Fit",
    "¡": "Faa", "!": "Fat", "(": "Fpa", ")": "Fpt", "[": "Fca", "]": "Fct",
    "{": "Fla", "}": "Flt", "«": "Fra", "»": "Frc", "“": "Fra", "”": "Frc",
    "‘": "Fra", "’": "Frc", "...": "Fs", "…": "Fs", "%": "Ft",
}

# FreeLing lemmas for personal pronouns (spaCy lemmatizes most of them as "él")
PERSONAL_PRONOUN_LEMMAS = {
    "yo": "yo", "me": "me", "mí": "mí", "conmigo": "conmigo",
    "tú": "tú", "te": "te", "ti": "ti", "contigo": "contigo", "vos": "vos",
    "él": "él", "ella": "él", "ello": "él", "ellos": "él", "ellas": "él",
    "lo": "lo", "la": "lo", "los": "lo", "las": "lo", "le": "le", "les": "le",
    "se": "se", "sí": "sí", "consigo": "consigo",
    "nosotros": "nosotros", "nosotras": "nosotros", "nos": "nos",
    "vosotros": "vosotros", "vosotras": "vosotros", "os": "os",
    "usted": "usted", "ustedes": "usted",
}

CLITIC_PRONOUNS = {"me", "te", "se", "lo", "la", "le", "nos", "os", "los", "las", "les"}

# case of personal pronouns when spaCy does not provide it (as FreeLing tags them)
_PRONOUN_CASE = {
    "lo": "A", "la": "A", "los": "A", "las": "A", "le": "D", "les": "D",
    "yo": "N", "tú": "N", "vos": "N", "él": "N", "ella": "N", "ellos": "N", "ellas": "N",
    "nosotros": "N", "nosotras": "N", "vosotros": "N", "vosotras": "N",
    "mí": "O", "ti": "O", "sí": "O", "conmigo": "O", "contigo": "O", "consigo": "O",
}

_PRONOUN_PERSON = {
    "yo": "1", "me": "1", "mí": "1", "conmigo": "1", "nosotros": "1", "nosotras": "1", "nos": "1",
    "tú": "2", "te": "2", "ti": "2", "contigo": "2", "vos": "2", "vosotros": "2", "vosotras": "2",
    "os": "2",
}

NEUTER_PRONOUNS = {"esto", "eso", "aquello", "ello", "lo"}

NUMBER_WORDS = {
    "cero": "0", "uno": "1", "una": "1", "un": "1", "dos": "2", "tres": "3", "cuatro": "4",
    "cinco": "5", "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
    "once": "11", "doce": "12", "trece": "13", "catorce": "14", "quince": "15",
    "dieciséis": "16", "diecisiete": "17", "dieciocho": "18", "diecinueve": "19", "veinte": "20",
    "treinta": "30", "cuarenta": "40", "cincuenta": "50", "sesenta": "60", "setenta": "70",
    "ochenta": "80", "noventa": "90", "cien": "100", "ciento": "100", "mil": "1000",
}

AUXILIAR_LEMMAS = {"haber", "estar"}

SEMANTIC_CLASS_BY_ENT = {"PER": "SP", "PERSON": "SP", "LOC": "G0", "GPE": "G0",
                         "ORG": "O0", "MISC": "V0"}


def _first(value):
    # spaCy joins multiple values with "," (e.g. PronType=Int,Rel)
    return value.split(",")[0] if value else value


def _gender(feats, default="C"):
    return {"Masc": "M", "Fem": "F"}.get(_first(feats.get("Gender")), default)


def _number(feats, default="S"):
    return {"Sing": "S", "Plur": "P"}.get(_first(feats.get("Number")), default)


def is_relative(word):
    return "Rel" in (word.feats.get("PronType") or "").split(",")


def punctuation_tag(form):
    if form in PUNCTUATION_TAGS:
        return PUNCTUATION_TAGS[form]
    if form and all(char == "." for char in form):
        return "Fs"
    return "Fz"


def tag_of(word):
    """EAGLES tag for a Word (see freeling_tree.Word)."""
    if word.is_date:
        return "W"

    pos, feats, lower = word.pos, word.feats, word.form.lower()

    if pos in ("PUNCT", "SYM"):
        return punctuation_tag(word.form)

    if pos == "NUM" or (pos == "DET" and feats.get("NumType") == "Card"):
        return "Z"

    if pos == "PROPN" or (pos == "X" and word.form[:1].isupper()):
        return "NP00" + (word.semantic_class or "V0") + "0"

    if pos in ("NOUN", "X"):
        return "NC" + _gender(feats) + _number(feats) + "000"

    if pos in ("VERB", "AUX"):
        return verb_tag(word)

    if pos == "ADJ":
        kind = "O" if feats.get("NumType") == "Ord" else "Q"
        function = "P" if feats.get("VerbForm") == "Part" else "0"
        return "A" + kind + "0" + _gender(feats) + _number(feats) + function

    if pos == "DET":
        return determinant_tag(word)

    if pos == "PRON" or (word.relative_role and pos == "ADV"):
        return pronoun_tag(word)

    if pos == "ADV":
        return "RN" if lower == "no" else "RG"

    if pos == "ADP":
        if lower in ("del", "al"):
            return "SPCMS"
        return "SPS00"

    if pos == "CCONJ":
        return "CC"

    if pos == "SCONJ":
        return "CS"

    if pos == "INTJ":
        return "I"

    return "NC" + _gender(feats) + _number(feats) + "000"


def verb_tag(word):
    feats, lemma = word.feats, word.lemma
    kind = "A" if lemma in AUXILIAR_LEMMAS else ("S" if lemma == "ser" else "M")
    form = _first(feats.get("VerbForm"))

    if form == "Inf":
        return "V" + kind + "N0000"
    if form == "Ger":
        return "V" + kind + "G0000"
    if form == "Part":
        gender = {"Masc": "M", "Fem": "F"}.get(_first(feats.get("Gender")), "M")
        return "V" + kind + "P00" + _number(feats) + gender

    mood = _first(feats.get("Mood"))
    tense = _first(feats.get("Tense"))
    mode = {"Ind": "I", "Sub": "S", "Imp": "M", "Cnd": "I"}.get(mood, "I")
    if mood == "Cnd":
        time = "C"
    else:
        time = {"Pres": "P", "Imp": "I", "Past": "S", "Fut": "F"}.get(tense, "P")
    person = _first(feats.get("Person")) if _first(feats.get("Person")) in ("1", "2", "3") else "3"
    return "V" + kind + mode + time + person + _number(feats) + "0"


def determinant_tag(word):
    feats, lower = word.feats, word.form.lower()
    pron_type = _first(feats.get("PronType"))
    kind = {"Art": "A", "Dem": "D", "Prs": "P", "Int": "T", "Exc": "E"}.get(pron_type, "I")
    if feats.get("Poss") == "Yes":
        kind = "P"

    person = "0"
    owner = "0"
    if kind == "P":
        person = _first(feats.get("Person")) if _first(feats.get("Person")) in ("1", "2", "3") else "3"
        owner = {"Sing": "S", "Plur": "P"}.get(_first(feats.get("Number[psor]")), "S")

    gender = "N" if lower == "lo" else _gender(feats)
    return "D" + kind + person + gender + _number(feats) + owner


def pronoun_tag(word):
    feats, lower = word.feats, word.form.lower()
    pron_type = _first(feats.get("PronType"))

    if word.relative_role:
        kind = "R"
    else:
        kind = {"Prs": "P", "Dem": "D", "Ind": "I", "Tot": "I", "Neg": "I", "Int": "T",
                "Rel": "R", "Exc": "E"}.get(pron_type, "P" if lower in PERSONAL_PRONOUN_LEMMAS else "I")
        if feats.get("Poss") == "Yes":
            kind = "X"

    if kind == "R":
        person = "0"
    else:
        person = _first(feats.get("Person")) if _first(feats.get("Person")) in ("1", "2", "3") \
            else _PRONOUN_PERSON.get(lower, "3" if kind == "P" else "0")

    if lower in NEUTER_PRONOUNS and lower != "lo":
        gender = "N"
    elif lower in ("me", "te", "se", "nos", "os", "le", "les", "yo", "tú", "mí", "ti", "sí", "que"):
        gender = "C"
    else:
        gender = _gender(feats)

    if lower in ("se", "que"):
        number = "N"
    else:
        number = {"Sing": "S", "Plur": "P"}.get(_first(feats.get("Number")), "N" if kind == "R" else "S")

    case = "0"
    if kind == "P":
        case = {"Nom": "N", "Acc": "A", "Dat": "D"}.get(_first(feats.get("Case")), "")
        case = case or _PRONOUN_CASE.get(lower, "0")
        if lower in ("me", "te", "se", "nos", "os"):
            case = "0"

    politeness = "P" if lower in ("usted", "ustedes", "vos") else "0"
    return "P" + kind + person + gender + number + case + "0" + politeness


def lemma_of(word):
    lower = word.form.lower()

    if word.pos in ("PUNCT", "SYM"):
        return word.form

    if word.pos == "PRON" and lower in PERSONAL_PRONOUN_LEMMAS:
        return PERSONAL_PRONOUN_LEMMAS[lower]

    if word.pos == "NUM" or (word.pos == "DET" and word.feats.get("NumType") == "Card"):
        return NUMBER_WORDS.get(lower, lower)

    if word.pos == "PROPN" or word.merged:
        return lower

    lemma = (word.lemma or lower).lower()
    # spaCy may lemmatize verbs with enclitics as "decir él"; FreeLing keeps the verb lemma only
    return lemma.split()[0] if lemma.split() else lower


# --------------------------------------------------------------------------------------------------
# Choosing among the analyses of the FreeLing dictionary
# --------------------------------------------------------------------------------------------------

# spaCy coarse part of speech -> EAGLES tag prefixes it can correspond to
COMPATIBLE_PREFIXES = {
    "NOUN": ("NC",), "VERB": ("V",), "AUX": ("V",), "ADJ": ("A", "VMP"), "DET": ("D", "Z"),
    "PRON": ("P",), "ADV": ("R",), "ADP": ("S",), "CCONJ": ("CC",), "SCONJ": ("CS",), "NUM": ("Z",),
    "INTJ": ("I",),
}

POS_BY_CATEGORY = {"P": "PRON", "D": "DET", "S": "ADP", "C": "CCONJ", "V": "VERB", "N": "NOUN",
                   "A": "ADJ", "R": "ADV", "I": "INTJ", "Z": "NUM", "F": "PUNCT", "W": "NOUN"}

CLOSED_CLASSES = ("P", "D", "S", "C")


def pos_for_tag(tag):
    if tag.startswith("CS"):
        return "SCONJ"
    if tag.startswith("NP"):
        return "PROPN"
    return POS_BY_CATEGORY.get(tag[0], "X")


def _similarity(candidate, generated):
    return sum(1 for a, b in zip(candidate, generated) if a == b) + (5 if candidate[:2] == generated[:2] else 0)


def choose_analysis(word, analyses):
    """The FreeLing (lemma, tag) that best fits spaCy's part of speech and morphology, or None."""
    if not analyses or word.pos in ("PROPN", "PUNCT", "SYM", "X") or word.is_date or word.merged:
        return None
    generated = tag_of(word)
    prefixes = COMPATIBLE_PREFIXES.get(word.pos, ())
    if word.relative_role:
        prefixes = ("PR",) + prefixes
    if word.pos == "ADJ" and word.feats.get("VerbForm") == "Part":
        prefixes = ("VMP",) + prefixes
    for prefix in prefixes:
        candidates = [analysis for analysis in analyses if analysis[1].startswith(prefix)]
        if candidates:
            return max(candidates, key=lambda analysis: _similarity(analysis[1], generated))
    return None


def closed_class_correction(word, analyses):
    """spaCy sometimes takes a pronoun or a determiner for a verb or a noun ("nosotras" -> VERB).
    When every FreeLing analysis of the form is a closed class word, the part of speech is fixed."""
    if word.pos not in ("VERB", "NOUN", "ADJ", "PROPN", "X") or not analyses:
        return None
    categories = set(tag[0] for _, tag in analyses)
    if not categories <= set(CLOSED_CLASSES):
        return None
    if any(tag.startswith(prefix) for _, tag in analyses for prefix in COMPATIBLE_PREFIXES.get(word.pos, ())):
        return None
    return pos_for_tag(sorted(analyses, key=lambda analysis: analysis[1])[0][1])
