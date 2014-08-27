# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

#Must have .../xmlrpc.php
HOST = ''
USER = ''
PASS = ''


class BlogPublisher(object):

	def __init__(self, text, links):
		# TODO: placeholder, hasta tener  
		self.text = text
		self.links = links

	def publish(self):
		entry = self._generate_entry()
		self._publish_entry(entry)

	def _generate_entry(self):
		html_links = self._format_html_links()
		content = self._add_links_to_text(html_links)
		entry = Entry(self._get_title(), content, self._get_tags(), self._get_source())
		return 

	def _publish_entry(self, entry):
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

	def _format_html_links(self):
		html_links = []
		for link in self.links:
			#TODO: cambiar el texto del link
			html_links.append("<a href=%s>%s</a>" % (link, link))
		return html_links

	def _add_links_to_text(self, html_links):
		pass

	def _get_title(self):
		return ''

	def _get_tags(self):
		return []

	def _get_source(self):
		return ''

class Entry(object):
	def __init__(self, title, content, tags, source):
		self.title = title
		self.content = content
		self.tags = tags
		self.source = source