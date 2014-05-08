#-*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from codecs import open
from os.path import join

def load_namelists():
    config = ConfigParser()
    config.read("config")
    directory = join(dict(config.items("resources"))["resources_dir"], "gender_detection")

    names = {}

    names["male"] = set([ line.split(',')[0] for line in
                         open(join(directory, "male.txt"), 'r', 'utf-8').readlines() ])
    names["female"] = set([ line.split(',')[0] for line in
                           open(join(directory, "female.txt"), 'r', 'utf-8').readlines() ])

    names["neutral"] = set()

    unisex_names_with_gender = [ (line.split(',')[0], line.split(',')[2]) for line in
                                open(join(directory, "unisex.csv"), 'r', 'utf-8').readlines() ]

    for name, gender in unisex_names_with_gender:
        if gender in names:
            names[gender].add(name)
        if name not in names["male"] and name not in names["female"]:
            names["neutral"].add(name)

    return names

class GenderDetector:

    def gender_of(self, name):
        name = name.upper()

        gender_preference = [ "male", "female", "neutral" ]
        for gender in gender_preference:
            if name in GenderDetector.names_by_gender[gender]:
                return { "male" : "masculine", "female" : "feminine", "neutral" : "neutral" }[gender]
        return None

    names_by_gender = load_namelists()