from pymongo import MongoClient
import ConfigParser


class MongoConnector(object):
    __db = None

    @classmethod
    def get_instance(cls, mode=None):
        if MongoConnector.__db is None:
            config = ConfigParser.ConfigParser()
            config.read('config')
            client = MongoClient(config.get('mongodb', 'host'),
                                 int(config.get('mongodb', 'port')))
            if not mode is None and mode == 'test':
                MongoConnector.__db = client[config.get('mongodb', 'db_test')]
            else:
                MongoConnector.__db = client[config.get('mongodb', 'db')]

        return MongoConnector.__db


