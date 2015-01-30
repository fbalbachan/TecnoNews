import unittest

class Dev(object):

	def __init__(self):
		print 'init dev'

	def code(self):
		self.do_my_shit()


class Pablo(Dev):
	def __init__(self):
		Dev.__init__(self)

	def do_my_shit(self):
		print 'this is the pablo \'s shit'


if __name__ == '__main__':
	Pablo().code()