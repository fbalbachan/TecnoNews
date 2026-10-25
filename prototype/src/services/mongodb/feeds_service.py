from .connector import MongoConnector
from src.sentinews.feeds import Feed


class FeedService(object):
    COLLECTION = 'feeds'

    def __init__(self):
        self.db = MongoConnector.get_instance()
        self.feeds = self.db[FeedService.COLLECTION]

    def save(self, feed):
        return self.feeds.insert_one(feed.to_dict()).inserted_id

    def get_all(self):
        return [Feed(feed['id'], feed['url'], feed['parser'], feed['lastupdated'],
                     feed['default_tags'] if 'default_tags' in feed else None)
                for feed in self.feeds.find({})]

    def get_feeds_to_process(self, list_of_feeds):
        return [Feed(feed['id'], feed['url'], feed['parser'], feed['lastupdated'],
                     feed['default_tags'] if 'default_tags' in feed else None)
                for feed in self.feeds.find({"id":  {"$in": list_of_feeds}})]

