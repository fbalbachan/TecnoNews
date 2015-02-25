# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *
import ConfigParser

logger = get_logger('tecnonews')


class BlogPublisher(object):

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('config')

    def publish(self, entry, test=False):
        # TODO: simplify this method extract formating logic of each section to new methods
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
        host = self.select_category_to_publish(entry)
        client = Client(host['url'], host['username'], host['password'])
        # Post new entry
        wp_id = client.call(NewPost(post))
        # Get the just posted wordpress entry and save the url
        if wp_id:
            wp_url = client.call(GetPost(wp_id)).link
        else:
            logger.error("not wp_id %s" % wp_id)
            wp_url = ""

        return wp_id, wp_url

    def get_category_host_to_publish(self):
        import json
        user_per_categories_file = self.config.get('publishing', 'category_host_to_publish')

        with open(user_per_categories_file) as f:
            categories_host = json.loads(f.read())
        return categories_host

    def get_categories_priority(self):
        import json
        categories_priority_file = self.config.get('publishing', 'categories_priority')

        with open(categories_priority_file) as f:
            categories_priority = json.loads(f.read())
        return categories_priority

    def select_category_to_publish(self, entry):
        assert entry.categories

        categories_hosts = self.get_category_host_to_publish()
        categories_priority = self.get_categories_priority()

        selected_host = None

        for category in categories_priority:
            if category in entry.categories:
                selected_host = categories_hosts[category]
                break

        assert selected_host

        return selected_host
