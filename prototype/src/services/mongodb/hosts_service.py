from src.services.mongodb.connector import MongoConnector

class HostsService(object):
    COLLECTION = 'hosts'

    def __init__(self, mode=None):
        self.db = MongoConnector.get_instance(mode)
        self.hosts = self.db[HostsService.COLLECTION]
      
    def get_list(self, criteria, limit=None):
        """ Retrieve a list of new entries
        Parameters
        ----------
        criteria: dict
        this is the object to use on mongodb find statement
        """
        return [entry for entry in self.hosts.find(criteria).limit(limit if limit is not None else 0)]
