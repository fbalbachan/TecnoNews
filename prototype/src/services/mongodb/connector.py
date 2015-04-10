from pymongo import MongoClient
from src.utils.configProvider import ConfigProvider


class MongoConnector(object):
    __db = None

    @classmethod
    def get_instance(cls, mode=None):
        if MongoConnector.__db is None:
            config = ConfigProvider()
            client = MongoClient(config.get('mongodb', 'host'),
                                 int(config.get('mongodb', 'port')))
            if not mode is None and mode == 'test':
                MongoConnector.__db = client[config.get('mongodb', 'db_test')]
            else:
                MongoConnector.__db = client[config.get('mongodb', 'db')]

        return MongoConnector.__db

    @classmethod
    def get_db_name(cls):
        config = ConfigProvider()
        return config.get('mongodb', 'db')

    @classmethod
    def clone_test_db(cls):

        config = ConfigProvider()
        # production = config.get('mongodb', 'db')
        # test = config.get('mongodb', 'db_test')
        production = 'sentinews'
        testing = 'sentinews_test'
        client = MongoClient(config.get('mongodb', 'host'),
                                 int(config.get('mongodb', 'port')))

        client.drop_database(testing)
        client.admin.command('copydb',
                         fromdb=production,
                         todb=testing)