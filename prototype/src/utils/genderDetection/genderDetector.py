# -*- coding: utf-8 -*-
from src.ling.genderEnum import GenderEnum
from src.utils.configProvider import ConfigProvider
from codecs import open
from os.path import join
from unidecode import unidecode


def load_name_lists():
    config = ConfigProvider()
    directory = join(dict(config.items("resources"))["resources_dir"], "gender_detection")

    male_lines = open(join(directory, "male.txt"), 'r', 'utf-8').readlines()
    female_lines = open(join(directory, "female.txt"), 'r', 'utf-8').readlines()

    names = {"male":    set([unidecode(line.split(',')[0]) for line in male_lines]),
             "female":  set([unidecode(line.split(',')[0]) for line in female_lines]),
             "neutral": set()}

    unisex_lines = open(join(directory, "unisex.csv"), 'r', 'utf-8').readlines()
    unisex_names_with_gender = [(unidecode(line.split(',')[0]), unidecode(line.split(',')[2])) for line in unisex_lines]

    for name, gender in unisex_names_with_gender:
        if gender in names:
            names[gender].add(name)

        if name not in names["male"] and name not in names["female"]:
            names["neutral"].add(name)

    return names


class GenderDetector:

    def gender_of(self, name):
        name = unidecode(name.decode("utf-8")).upper()

        gender_preference = ["male", "female", "neutral"]
        for gender in gender_preference:
            if name in GenderDetector.names_by_gender[gender]:
                gender_map = {"male": GenderEnum.masculine,
                              "female": GenderEnum.feminine,
                              "neutral": GenderEnum.neutral}
                return gender_map[gender]
        return None

    names_by_gender = load_name_lists()