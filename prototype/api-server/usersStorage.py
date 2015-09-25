# -*- coding: utf-8 -*-

from datetime import datetime, date
from src.utils.csvwrapper import unicode_csv_reader, unicode_csv_writer

__author__ = 'Martín Caramés Abente'


class UsersStorage(object):

    def __init__(self):
        self._last_refresh_date = datetime.min
        self._users = dict()

    def get_users(self):

        if self._users:
            time_to_last_refresh = abs(datetime.now() - self._last_refresh_date)
            if time_to_last_refresh.total_seconds() > 120:
                users_on_storage = UsersStorage.deserialize()
                self._users = self.merge_users_data(self._users, users_on_storage)
                self.serialize()
                self._last_refresh_date = datetime.now()
        else:
            self._users = UsersStorage.deserialize()

        return self._users

    @staticmethod
    def deserialize():
        users_file = "./users.csv"
        users_file_reader = unicode_csv_reader(open(users_file, 'r'), first_line_is_header=False, delimiter=',')
        users = dict()

        for auth_token, name, mail, organization, access_counter, issuing_date in users_file_reader:
            user = dict()
            user["name"] = name
            user["mail"] = mail
            user["organization"] = organization
            user["access_counter"] = int(access_counter)
            user["issuing_date"] = datetime.strptime(issuing_date, "%Y%m%d")
            users[auth_token] = user

        return users

    def serialize(self):
        if not self._users:
            return

        rows = []
        for token in self._users.keys():
            user = self._users[token]
            row = [token,
                   user["name"],
                   user["mail"],
                   user["organization"],
                   str(user["access_counter"]),
                   user["issuing_date"].strftime("%Y%m%d")]
            print row
            rows = rows + [row]

        unicode_csv_writer(rows, open("./users.csv", 'w'))

    def merge_users_data(self, users_on_cache, users_on_storage):
        new_users = dict()
        for token in users_on_storage.keys():
            user_on_storage = users_on_storage[token]
            new_user = user_on_storage
            storage_counter = users_on_storage[token]["access_counter"]

            if token in users_on_cache:
                new_user["access_counter"] = max(users_on_cache[token]["access_counter"], storage_counter)
                new_user["issuing_date"] = users_on_storage[token]["issuing_date"] or \
                                         users_on_cache[token]["issuing_date"]

            new_users[token] = new_user

        for token in users_on_cache.keys():
            user_on_cache = users_on_cache[token]
            new_user = user_on_cache
            if token in users_on_storage:
                cache_counter = users_on_cache[token]["access_counter"]
                new_user["access_counter"] = max(users_on_storage[token]["access_counter"], cache_counter)
                new_user["issuing_date"] = users_on_storage[token]["issuing_date"] or \
                                           users_on_cache[token]["issuing_date"]

                new_users[token] = new_user

        return new_users

    def is_valid_token(self, api_key):
        return api_key in self.get_users().keys()

    def get_user(self, api_key):
        return self.get_users()[api_key]

    def get_issuing_date(self, api_key):
        return self.get_user(api_key)["issuing_date"]

    def get_access_counter(self, api_key):
        return self.get_user(api_key)["access_counter"]

    def increase_access_counter(self, api_key):
        user = self.get_user(api_key)
        ac = user["access_counter"]
        print "ac before = ", user["access_counter"]
        user["access_counter"] = ac + 1
        print "ac after = ", user["access_counter"]

    def has_expired(self, api_key):
        time_passed = abs(datetime.now() - self.get_issuing_date(api_key))
        return time_passed.days > 30 or self.get_access_counter(api_key) >= 500


users_storage = UsersStorage()
