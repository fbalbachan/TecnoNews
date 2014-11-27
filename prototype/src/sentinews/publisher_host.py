# -*- coding: utf-8 -*-
class WPHost(object):

	def __init__(self, host, user, password):
		self.host = host
		self.user = user
		self.password = password

	def __hash__(self):
		return hash(self.host + self.user + self.password)


	def __cmp__(self, other):
		return cmp(self.host, other.host) and cmp(self.user, other.user) and cmp(self.password, other.password)