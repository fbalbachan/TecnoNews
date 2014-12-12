# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import taxonomies
from src.sentinews.news_entry import NewsEntry
import ConfigParser
from src.sentinews.categorizer import *


class BlogPublisher(object):

	def publish(self, entry):
		post = WordPressPost()
		post.title = entry.title
		post.content = entry.content
		#post.content += "<br><br><strong> Fuente: " + entry.source + "</strong>"
		post.terms_names = {
                  'category': entry.categories
		}
		post.post_status = 'publish'
		client = None
		for host in entry.destination:
			client = Client(host.host, host.user, host.password )
			client.call(NewPost(post))

                
