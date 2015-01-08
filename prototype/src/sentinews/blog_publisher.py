# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import taxonomies
from src.sentinews.news_entry import NewsEntry
import ConfigParser
from src.sentinews.categorizer import *
from src.services.mongodb.news_entries_service import NewsEntriesService


class BlogPublisher(object):

	def publish(self, entry, test=False):
		news_service = NewsEntriesService() if not test else NewsEntriesService('test')
		post = WordPressPost()
		post.title = entry.title
		post.content = entry.content

		if len(entry.related) > 0:
			post.content += "<br><br><strong> La misma noticia en otras coberturas:</strong>"
			post.content += '<ul>'
			for related_news_id in entry.related:
				unmarshalled_news = news_service.get_list({'_id': related_news_id})
				if len(unmarshalled_news) == 1:
					post.content += '<li><a href="' + unmarshalled_news[0].wp_url + '">'
					post.content += unmarshalled_news[0].title +'</a></li>'

			post.content += '</ul>'
		post.terms_names = {
                  'category': entry.categories
		}
		post.post_status = 'publish'
		client = None
		for host in entry.destination:
			client = Client(host.host, host.user, host.password )
			entry.wp_id = client.call(NewPost(post))

                
