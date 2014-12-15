import ConfigParser
from src.services.mongodb.news_entries_service import NewsEntriesService 

class Crawler(object):
    
    def _filter_entries(self, entries):
        ''' Filter entries that already exist in the DB,
            we dont want to parse them again. '''
        service = NewsEntriesService()
        return [entry for entry in entries 
        if len(service.get_list({'title': unicode(entry.title)})) == 0]

    def _filter_by_tag(self, news_entries):
        Config = ConfigParser.ConfigParser()
        Config.read("config")

        tags_filename =  Config.get("resources", "tags_to_filter")
        with open(tags_filename) as tagsfile:
            tags = [tag.strip().lower() for tag in tagsfile]
        return [entry for entry in news_entries if  len(set(tags) & set([tag.lower() for tag in entry.tags])) == 0]
