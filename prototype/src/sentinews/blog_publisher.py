# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import taxonomies
from src.sentinews.news_entry import NewsEntry
import ConfigParser


class BlogPublisher(object):

	def __init__(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read('config')
		host, user, password = self.config.get('wordpress', 'host'), self.config.get('wordpress', 'user'), \
			self.config.get('wordpress', 'pass') 
		print host
		print user
		print password
		self.client = Client(host, user, password) 

	def publish(self, entry):
		post = WordPressPost()
		post.title = entry.title
		post.content = entry.content
		post.content += "<br><br><strong> Fuente: " + entry.source + "</strong>"
		post.terms_names = {
		  'post_tag': entry.tags,
		  'category': ['testcat', 'testcat2']
		}
		post.post_status = 'publish'
		self.client.call(NewPost(post))


	def get_categories(self):

		return self.client.call(taxonomies.GetTerms('category'))
