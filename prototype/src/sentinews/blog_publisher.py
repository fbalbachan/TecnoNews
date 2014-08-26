# -*- coding: utf-8 -*-

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
		return self._add_links_to_text(html_links)

	def _publish_entry(self, entry):
		pass

	def _format_html_links(self):
		html_links = []
		for link in self.links:
			#TODO: cambiar el texto del link
			html_links.append("<a href=%s>%s</a>" % (link, link))
		return html_links

	def _add_links_to_text(self, html_links):
		pass



