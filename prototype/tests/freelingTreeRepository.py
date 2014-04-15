# -*- coding: utf-8 -*-
from os import listdir
from os.path import join
import sha

from src.parser.freelingTreeParser import FreelingTreeParser
from src.utils.freelingClientParser import FreelingClientParser


class FreelingTreeRepository:
    def __init__(self, search_directory = "./"):
        self.search_directory = search_directory
        self.tree_parser = FreelingTreeParser()
        self.client_parser = FreelingClientParser()

    def from_text(self, text):
        text_hash = sha.new(text).hexdigest()
        path = join(self.search_directory, text_hash)
        if not text_hash in listdir(self.search_directory):
            output = "\n".join(self.client_parser.parse(text))
            tree_file = open(path, "w")
            tree_file.write(output)
            tree_file.close()

        return self.tree_parser.from_file(path)
