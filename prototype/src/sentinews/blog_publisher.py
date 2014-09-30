# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from src.sentinews.news_entry import NewsEntry

#Must have .../xmlrpc.php
HOST = 'http://tecnonews.comule.com/xmlrpc.php'
USER = 'tecnonews'
PASS = 'tecnonews1'


class BlogPublisher(object):

	def publish(self, entry):
		wp = Client(HOST, USER, PASS)
		post = WordPressPost()
		post.title = entry.title
		post.content = entry.content
		post.content += "<br> Fuente: " + entry.source
		post.terms_names = {
		  'post_tag': entry.tags
		}
		post.post_status = 'publish'
		wp.call(NewPost(post))