# -*- coding: utf-8 -*-
class WPHost(object):

	def __init__(self, host, user, password):
		self.host = host
		self.user = user
		self.password = password

	def __hash__(self):
		return hash(self.host + self.user + self.password)


	def __eq__(self, other):
		return (self.host, self.user, self.password) == (other.host, other.user, other.password)