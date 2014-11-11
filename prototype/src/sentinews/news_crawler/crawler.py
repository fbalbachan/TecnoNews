import sqlite3
import ConfigParser

class Crawler(object):
    
    def _filter_entries(self, entries):
        ''' Filter entries that already exist in the DB,
            we dont want to parse them again. '''
        cursor = sqlite3.connect("news_crawler.db").cursor()
        titles = cursor.execute("SELECT title FROM original_news_entries").fetchall()
        titles = [title[0] for title in titles]
        return [entry for entry in entries if entry['title'] not in titles]

    def _filter_by_tag(self, news_entries):
        Config = ConfigParser.ConfigParser()
        Config.read("config")

        tags_filename =  Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tagsfile:
            tags = [tag.strip().lower() for tag in tagsfile]
        return [entry for entry in news_entries if  len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]
