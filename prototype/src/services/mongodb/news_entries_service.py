from connector import MongoConnector
from src.sentinews.news_entry import NewsEntry


class NewsEntriesService(object):
    COLLECTION = 'news_entries'

    def __init__(self, mode=None):
        self.db = MongoConnector.get_instance(mode)
        self.news_entries = self.db[NewsEntriesService.COLLECTION]

    def save(self, news_entry):
        """ this method returns the objectId assigned"""

        return self.news_entries.insert(news_entry.to_dict())

    def remove_all(self):
        return self.news_entries.remove({})

    def get_list(self, criteria, limit=None):
        """ Retrieve a list of new entries
        Parameters
        ----------
        criteria: dict
        this is the object to use on mongodb find statement
        """
        return [NewsEntry(title=entry['title'], content=entry['content'],
                          tags=entry['tags'], source=entry['source'], url=entry['url'],
                          categories=entry['categories'],
                          published_date=entry['published_date'],
                          entities=entry['entities'],
                          wp_id=entry['wp_id'] if 'wp_id' in entry else None,
                          related=entry['related'] if 'related' in entry else None,
                          object_id=entry['_id'],
                          versions=entry['versions'] if 'versions' in entry else None)
                for entry in self.news_entries.find(criteria).limit(limit if limit is not None else 0)]

    def already_in_db(self, url):
        """ Return true
         | false
        Parameters
        ----------
        criteria: dict
        this is the object to use on mongodb find statement
        """
        criteria = dict(url=url)

        return len([entry for entry in self.news_entries.find(criteria)]) > 0

    def get_by_date_range(self, start=None, to=None, limit=None):
        """ Retrieve a list of a news_entries by a given date UTC rage
        Parameters
        ----------
        start: datetime
            date to start
        to: date
            date to finish
        """
        return self.get_list({'published_date': {'$gte': start, '$lte': to}}, limit)

    def get_by_categories(self, categories, limit=None):
        """ Retrieve a list of news_entries by a given categories array, at least one element would match
        Parameters
        ----------
        categories: list
            list of searched categories
        """
        return self.get_list({'categories': {'$in': categories}}, limit)

    def get_by_categories_date_range(self, fromDate, toDate, categories, limit=None):
        """Retrieve a list of news entries by a given categories array and date range
        Parameters
        ----------
        start: date
            date to start from
        to: date
            date to stop
        categories: list
            list of searched categories
        """
        from bson.objectid import ObjectId
        dummy_id_from = ObjectId.from_datetime(fromDate)
        dummy_id_to = ObjectId.from_datetime(toDate)
        # TODO: use dummy_id_to
        return self.get_list({"_id": {"$gt": dummy_id_from},
                              'categories': {'$in': categories}},
                             limit)