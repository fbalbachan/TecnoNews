# -*- coding: utf-8 -*-
from os import listdir
from os.path import join
import hashlib

from src.parser.freelingTreeParser import FreelingTreeParser
from src.utils.spacyClientParser import SpacyClientParser


class FreelingTreeRepository:
    def __init__(self, search_directory = "./"):
        self.search_directory = search_directory
        self.tree_parser = FreelingTreeParser()
        self.client_parser = SpacyClientParser()

    def from_text(self, text):
        text_hash = hashlib.sha1(text.encode("utf-8")).hexdigest()
        path = join(self.search_directory, text_hash)
        if not text_hash in listdir(self.search_directory):
            output = "\n".join(self.client_parser.parse(text))
            tree_file = open(path, "w", encoding="utf-8")
            tree_file.write(output)
            tree_file.close()

        return self.tree_parser.from_file(path)
