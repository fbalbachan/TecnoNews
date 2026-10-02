# -*- coding: utf-8 -*-
DEFAULT_MODEL = "es_core_news_md"

_pipelines = {}


def model_name():
    try:
        from src.utils.configProvider import ConfigProvider
        return ConfigProvider().get("spacy", "model")
    except Exception:
        return DEFAULT_MODEL


def get_nlp(name=None):
    """Returns a (cached) spaCy pipeline. Loading a model takes seconds, so it is done once per process."""
    name = name or model_name()
    if name not in _pipelines:
        import spacy
        nlp = spacy.load(name)
        split_edge_dashes(nlp)
        _pipelines[name] = nlp
    return _pipelines[name]


def split_edge_dashes(nlp):
    """Dashes opening or closing an aside are glued to the words in news text ("-los cumplió ... estreno-"):
    split them off, as FreeLing did. Hyphens inside words ("espacio-tiempo") are left alone."""
    from spacy.util import compile_prefix_regex, compile_suffix_regex
    dashes = ["-", "–", "—"]
    nlp.tokenizer.prefix_search = compile_prefix_regex(list(nlp.Defaults.prefixes) + dashes).search
    nlp.tokenizer.suffix_search = compile_suffix_regex(list(nlp.Defaults.suffixes) + dashes).search
