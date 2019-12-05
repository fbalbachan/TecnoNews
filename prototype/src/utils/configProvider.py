import sys
import ConfigParser
from src.decorators.singleton import singleton

@singleton
class ConfigProvider(object):

    def __new__(cls):
        new_instance = object.__new__(cls)
        config = ConfigParser.ConfigParser()
        if len(sys.argv)==2:
            config.read(sys.argv[1])
        else:
            config.read("config")
        cls.cfg = config
        return new_instance

    def __init__(self):
        pass

    @classmethod
    def get(cls, section, value):
        """

        :param section: String
        :param value: String
        :return: String
        """
        return cls.cfg.get(section, value)

    @classmethod
    def items(cls, section):
        return cls.cfg.items(section)

    @classmethod
    def getint(cls, section, value):
        return cls.cfg.get(section, value)
