# -*- coding: utf-8 -*-
from src.utils.configProvider import ConfigProvider
from src.utils.csvwrapper import unicode_csv_reader
import warnings


class Categorizer(object):
    def __init__(self, tags):
        if len(tags) == 0:
            warnings.warn('Tags must not be empty!')

        self.tags = tags
        self.config = ConfigProvider()
        categories_file = self.config.get("resources", "categories")
        countries_file = self.config.get("resources", "countries")

        categories_reader = unicode_csv_reader(open(categories_file, 'r'), first_line_is_header=False, delimiter=',')

        self.categories_dict = {}
        for row in categories_reader:
            if not isinstance(row[0], unicode):
                category = unicode(row[0], 'utf-8')
            else:
                category = row[0]

            self.categories_dict[category] = [unicode(element, 'utf-8') for element in row if element != '']

        countries_reader = unicode_csv_reader(open(countries_file, 'r'), first_line_is_header=False, delimiter=',')

        self.countries_list = [unicode(country[0].lower(), 'utf-8') for country in countries_reader]
        self.categories = self.__create_categories()

    def get_or_else(self):
        return self.categories if self.categories is not None else []

    def __create_categories(self):
        categories = set([])
        if len(self.tags) > 0:
            for element in self.tags:
                for category, list_tags in self.categories_dict.iteritems():
                    for tag in list_tags:
                        ltag = tag.lower()
                        lelement = element.lower()

                        if lelement in self.countries_list:
                            categories.add('internacionales')
                        if lelement.find(ltag) > -1:
                            categories.add(category)

        if not categories:
            # If fails to categorize set default category
            categories = {u'interés general'}

        assert categories
        return categories
