# -*- coding: utf-8 -*-
# spaCy based replacement for the remote FreeLing / Sentilecto NLU server.
#
#   spacy_engine  -> loads the spaCy pipeline (config [spacy])
#   eagles        -> UD (spaCy) part of speech + morphology -> FreeLing EAGLES tags and lemmas
#   freeling_tree -> spaCy dependency parse -> FreeLing full-parse tree text (the format that
#                    src.parser.freelingTreeParser.FreelingTreeParser consumes)
