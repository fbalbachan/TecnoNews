# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *

logger = get_logger('tecnonews')


class BlogPublisher(object):
    def publish(self, entry, test=False):
        news_service = NewsEntriesService() if not test else NewsEntriesService('test')
        post = WordPressPost()
        post.title = entry.title
        post.content = entry.content

        if len(entry.versions) > 0:
            post.content += "<br><br><strong> La misma noticia en otras coberturas:</strong>"
            post.content += '<ul>'
            for version_news_id in entry.versions:
                unmarshalled_news = news_service.get_list({'_id': version_news_id})
                if len(unmarshalled_news) == 1:
                    post.content += '<li><a href="' + unmarshalled_news[0].wp_url + '">'
                    post.content += unmarshalled_news[0].title + '</a><span>&nbsp;'
                    post.content += unmarshalled_news[0].published_date.strftime('%B %d, %Y')
                    post.content += '</span>'

            post.content += '</ul>'

        if len(entry.related) > 0:
            post.content += '<br><br><strong> Noticias relacionadas:</strong>'
            post.content += '<ul>'
            for related_id in entry.related:
                unmarshalled_news = news_service.get_list({'_id': related_id})
                if len(unmarshalled_news) == 1:
                    post.content += '<li><a href="' + unmarshalled_news[0].wp_url + '">'
                    post.content += unmarshalled_news[0].title + '</a><span>&nbsp;'
                    post.content += unmarshalled_news[0].published_date.strftime('%B %d, %Y')
                    post.content += '</span>'
            post.content += '</ul>'

        post.terms_names = {
            'post_tag': entry.tags,
            'category': entry.categories
        }
        post.post_status = 'publish'

        # use only one host to publish for now the first but we must guarantee unicity
        host = entry.destination.pop()
        client = Client(host.host, host.user, host.password)
        # Post new entry
        wp_id = client.call(NewPost(post))
        # Get the just posted wordpress entry and save the url
        if wp_id:
            wp_url = client.call(GetPost(wp_id)).link
        else:
            logger.error("not wp_id %s" % wp_id)
            wp_url = ""

        return wp_id, wp_url

