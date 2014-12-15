from src.utils.textDistance import TextDistance
from src.utils.newsItem import NewsItem
# import ConfigParser


class TextSimilarityRank(object):

    def __init__(self, original, list_of_texts):
        self.text_distance = TextDistance()

        self.original = original
        # self.original_cleaned = NewsItem(original.file_name, self.clean_text(original.content), original.title)
        self.texts_to_compare = list_of_texts
        # self.texts_to_compare_cleaned = self.clean_texts(list_of_texts)

    def get_similarity_rank(self):
        return self.get_similarity_rank_original()

    # def load_stopwords(self):
    #     stopwords = []
    #     config = ConfigParser.ConfigParser()
    #     config.read("config")
    #
    #     stopwords_filename = config.get("resources", "stopwords_es_clean")
    #
    #     for line in open(stopwords_filename, 'r'):
    #         if line[0] not in ['<', '%', '\n']:
    #             stopwords.append(line.rstrip('\n'))
    #
    #     return stopwords

    def get_similarity_rank_entities(self):
        similarities = []

        for newsItem in self.texts_to_compare:
            similarity = TextDistance.relevant_entities_coincidence(self.original, newsItem)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_original(self):
        similarities = []

        for newsItem in self.texts_to_compare:
            similarity = self.text_distance.similarity(self.original.content, newsItem.content)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_content_lemmatized(self):
        similarities = []

        for newsItem in self.texts_to_compare:
            similarity = self.text_distance.similarity(self.original.content_lemmatized, newsItem.content_lemmatized)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_clean_content_lemmatized(self):
        similarities = []

        for newsItem in self.texts_to_compare:
            similarity = self.text_distance.similarity(self.original.clean_content_lemmatized,
                                                       newsItem.clean_content_lemmatized)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    def get_similarity_rank_cleaned(self):
        similarities = []

        for newsItem in text_to_compare:
            similarity = self.text_distance.similarity(original.clean_text, newsItem.clean_text)
            similarities.append([similarity, newsItem])

        return sorted(similarities, key=lambda x: x[0], reverse=True)

    # def clean_text(self, text):
    #     return ' '.join([w for w in text.split() if w not in self.stopwords])
    #
    # def clean_texts(self, newsItemList):
    #     clean_texts = []
    #     for item in newsItemList:
    #         clean_texts.append(NewsItem(item.file_name, self.clean_text(item.content), item.title))
    #
    #     return clean_texts

def save_test_data(original, to_compare):
    import pickle
    with open('original.pkl', 'wb') as output:
        pickle.dump(original, output, pickle.HIGHEST_PROTOCOL)

    with open('to_compare.pkl', 'wb') as output:
        pickle.dump(to_compare, output, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    # import os
    import pickle
    from src.utils.newsItem import NewsItem
    # from pprint import pprint
    # files = os.listdir('src/utils/texts/')
    # print files
    # original_file = files[-1]
    #
    # files.remove(original_file)
    # original = NewsItem.from_file('src/utils/texts/', original_file)
    #
    # text_to_compare = []
    #
    # for file_name in files:
    #     item = NewsItem.from_file('src/utils/texts/', file_name)
    #     text_to_compare.append(item)

    with open('original.pkl', 'rb') as input:
        original = pickle.load(input)

    original_file = original.file_name

    with open('to_compare.pkl', 'rb') as input:
        text_to_compare = pickle.load(input)
    tsr = TextSimilarityRank(original, text_to_compare)

    print "\n"
    print "similarity lemmatized filename original:", original_file
    for result in tsr.get_similarity_rank_content_lemmatized():
        print result[0], result[1].file_name

    print "\n"
    print "similarity filename original:", original_file

    for result in tsr.get_similarity_rank():
        print result[0], result[1].file_name

    print "\n"
    print "similarity filename original WO stopwords:", original_file

    for result in tsr.get_similarity_rank_cleaned():
        print result[0], result[1].file_name

    print "\n"
    print "similarity filename original WO stopwords lemmatized:", original_file

    for result in tsr.get_similarity_rank_clean_content_lemmatized():
        print result[0], result[1].file_name

    print "\n"
    print "similarity entities:", original_file

    for result in tsr.get_similarity_rank_entities():
        print result[0], result[1].file_name


