# -*- coding: utf-8 -*-

from datetime import datetime, date
from src.utils.csvwrapper import unicode_csv_reader, unicode_csv_writer

__author__ = 'Martín Caramés Abente'


debug_mode = False


class UsersStorage(object):

    _last_refresh_date = datetime.min

    def __init__(self):
        self._users = dict()

    def get_users(self):

        if self._users:
            if self.is_time_to_refresh():
                self.synchronize_cache_db()
        else:
            self._users = UsersStorage.deserialize()

        return self._users

    def synchronize_cache_db(self):
        if debug_mode: print "--> UsersStorage.synchronize_cache_db"
        users_on_storage = UsersStorage.deserialize()
        self._users = self.merge_users_data(self._users, users_on_storage)
        self.serialize()
        UsersStorage._last_refresh_date = datetime.now()
        if debug_mode: print "<-- UsersStorage.synchronize_cache_db"

    @staticmethod
    def deserialize():
        if debug_mode: print "--> UsersStorage.deserialize"
        users_file = "./users.csv"
        users_file_reader = unicode_csv_reader(open(users_file, 'r'), first_line_is_header=False, delimiter=',')

        users = dict()
        for row in list(users_file_reader):
            if len(row) < 8:
                print "This line has a wrong format, ignoring. Line: ", row
                continue

            auth_token = row[0]
            name = row[1]
            mail = row[2]
            organization = row[3]
            access_counter = row[4]
            max_allowed_accesses = row[5]
            issuing_date = row[6]
            last_access_date = row[7]

            user = dict()
            user["name"] = name
            user["mail"] = mail
            user["organization"] = organization
            user["access_counter"] = int(access_counter)
            user["max_allowed_accesses"] = int(max_allowed_accesses)
            user["issuing_date"] = datetime.strptime(issuing_date, "%Y-%m-%d")
            user["last_access_date"] = datetime.strptime(last_access_date, "%Y-%m-%d")
            users[auth_token] = user

        if debug_mode: print "<-- UsersStorage.deserialize"
        return users

    def serialize(self):
        if debug_mode: print "--> UsersStorage.serialize"
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
                   str(user["max_allowed_accesses"]),
                   user["issuing_date"].strftime("%Y-%m-%d"),
                   user["last_access_date"].strftime("%Y-%m-%d")]

            rows = rows + [row]

        unicode_csv_writer(rows, open("./users.csv", 'w'))
        if debug_mode: print "<-- UsersStorage.serialize"

    def merge_users_data(self, users_on_cache, users_on_storage):
        if debug_mode: print "--> UsersStorage.merge_users_data"

        new_users = dict()
        for token in users_on_storage.keys():
            user_on_storage = users_on_storage[token]
            new_user = user_on_storage

            if token in users_on_cache:
                new_user["access_counter"] = max(users_on_storage[token]["access_counter"],
                                                 users_on_cache[token]["access_counter"])

                new_user["max_allowed_accesses"] = max(users_on_storage[token]["max_allowed_accesses"],
                                                     users_on_cache[token]["max_allowed_accesses"])

                diff = users_on_storage[token]["issuing_date"] - users_on_cache[token]["issuing_date"]
                new_user["issuing_date"] = users_on_storage[token]["issuing_date"] if diff.seconds > 0 \
                                           else users_on_cache[token]["issuing_date"]

                diff = users_on_storage[token]["last_access_date"] - users_on_cache[token]["last_access_date"]
                new_user["last_access_date"] = users_on_storage[token]["last_access_date"] if diff.seconds > 0 \
                                               else users_on_cache[token]["last_access_date"]
            new_users[token] = new_user

        for token in users_on_cache.keys():
            user_on_cache = users_on_cache[token]
            new_user = user_on_cache
            if token in users_on_storage:
                new_user["access_counter"] = max(users_on_storage[token]["access_counter"],
                                                 users_on_cache[token]["access_counter"])

                new_user["max_allowed_accesses"] = max(users_on_storage[token]["max_allowed_accesses"],
                                                     users_on_cache[token]["max_allowed_accesses"])

                diff = users_on_storage[token]["issuing_date"] - users_on_cache[token]["issuing_date"]
                new_user["issuing_date"] = users_on_storage[token]["issuing_date"] if diff.seconds > 0 \
                                           else users_on_cache[token]["issuing_date"]

                diff = users_on_storage[token]["last_access_date"] - users_on_cache[token]["last_access_date"]
                new_user["last_access_date"] = users_on_storage[token]["last_access_date"] if diff.seconds > 0 \
                                               else users_on_cache[token]["last_access_date"]

                new_users[token] = new_user

        if debug_mode: print "<-- UsersStorage.merge_users_data"
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
        if debug_mode: print "--> UsersStorage.increase_access_counter"
        user = self.get_user(api_key)
        ac = user["access_counter"]
        user["access_counter"] = ac + 1
        if debug_mode: print "<-- UsersStorage.increase_access_counter: result=", user["access_counter"]

    def update_last_access_date(self, api_key, last_access_date):
        if debug_mode: print "--> UsersStorage.update_last_access_date"
        user = self.get_user(api_key)
        user["last_access_date"] = last_access_date
        if debug_mode: print "<-- UsersStorage.update_last_access_date: result=", user["last_access_date"]

    def get_last_access_date(self, api_key):
        return self.get_user(api_key)["last_access_date"]

    def get_max_allowed_accesses(self, api_key):
        return self.get_user(api_key)["max_allowed_accesses"]

    def has_expired(self, api_key):
        time_passed = abs(datetime.now() - self.get_issuing_date(api_key))
        max_allowed_accesses = self.get_max_allowed_accesses(api_key)
        return self.get_access_counter(api_key) >= max_allowed_accesses
        #      or time_passed.days > 30

    def signal_refresh_occasion(self):
        if debug_mode: print "--> UsersStorage.signal_refresh_occasion"
        if self.is_time_to_refresh():
            self.synchronize_cache_db()
        if debug_mode: print "<-- UsersStorage.signal_refresh_occasion"

    def is_time_to_refresh(self):
        if debug_mode: print "--> UsersStorage.is_time_to_refresh"
        time_to_last_refresh = abs(datetime.now() - UsersStorage._last_refresh_date)
        is_time = time_to_last_refresh.total_seconds() > 60
        if debug_mode: print "--> UsersStorage.is_time_to_refresh: result=", str(is_time)
        return is_time

users_storage = UsersStorage()
