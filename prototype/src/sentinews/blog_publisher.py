# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost
from wordpress_xmlrpc.methods import media, posts
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *
from src.utils.configProvider import ConfigProvider
import urllib
from wordpress_xmlrpc.compat import xmlrpc_client
import mimetypes
from src.utils.SvgToPng import to_png

logger = get_logger('tecnonews')


class BlogPublisher(object):

    def __init__(self):
        self.config = ConfigProvider()

    def publish(self, entry, test=False):
        # TODO: simplify this method extract formatting logic of each section to new methods
        news_service = NewsEntriesService() if not test else NewsEntriesService('test')
        post = WordPressPost()
        post.title = entry.title
        post.content = entry.content

        # use only one host to publish for now the first but we must guarantee unicity
        host = self.select_category_to_publish(entry)
        logger.info("publishing into host %s" % host['url'])

        client = Client(host['url'], host['username'], host['password'])

        if entry.image:
            image_data = self.get_data_upload_image(entry.image)
            logger.info("image info %s" % image_data)

            response = client.call(media.UploadFile(image_data))
            # response == {
            #       'id': 6,
            #       'file': 'picture.jpg'
            #       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
            #       'type': 'image/jpeg',
            # }

            post.thumbnail = response['id']

        # Portada minimal logic
        logger.info("post.injected_count %s" % entry.injected_count)
        logger.info("post.thumbnail %s" % post.thumbnail)

        if entry.injected_count >= 2 and post.thumbnail:
            entry.categories.append("Portada")
            logger.info("Portada")

        post.terms_names = {
            'post_tag': entry.tags,
            'category': entry.categories
        }
        post.post_status = 'publish'

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

        if not selected_host:
            logger.error("Not Selected Host")
            logger.error("Categories %s " % entry.categories)

        assert selected_host

        return selected_host

    def get_data_upload_image(self, img):
        url = img['url']
        title = img['title']
        description = img['description']

        image = urllib.URLopener()
        tmp_filepath, o = image.retrieve(url)
        filename = url.split('/')[-1]
        filename_wo_extension = filename.split('.')[0]
        filename_extension = filename.split('.')[-1]

        # prepare metadata
        import re
        filename_wo_extension_safe = re.sub('[^A-Za-z0-9]+', '', filename_wo_extension)
        data = dict(name=filename_wo_extension_safe + '.' + filename_extension,
                    title=title,
                    description=description)

        #guess mimetype
        data['type'] = mimetypes.read_mime_types(filename) or mimetypes.guess_type(filename)[0]
        logger.info("Mimetype: %s" % data['type'])

        if data['type'] == 'image/svg+xml' or filename.split('.')[1] == 'svg':

            filename_png = filename_wo_extension_safe + '.png'

            svg = open(tmp_filepath).read()
            to_png(svg, '/tmp/' + filename_png)

            tmp_filepath = '/tmp/' + filename_png
            data['name'] = filename_png

        # read the binary file and let the XMLRPC library encode it into base64
        with open(tmp_filepath, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())

        return data

    def insert_canonical(self, entries, new_post_url):
        # TODO: workaround this hardcoded data
        user = 'emmettbrown'
        password = '6503b89221548c7cde2128570003d410'

        for entry in entries:
            url = entry.wp_url.split('.com')[0] + '.com/xmlrpc.php'
            client = Client(url, user, password)
            wpost = client.call(posts.GetPost(entry.wp_id))
            wpost.custom_fields = [dict(key='my_canonical', value=new_post_url)]
            client.call(posts.EditPost(entry.wp_id, wpost))
            logger.info("inserted cannonical in %s" % entry.wp_url)

    def remove_from_portada(self, entries):
        # TODO: workaround this hardcoded data
        user = 'emmettbrown'
        password = '6503b89221548c7cde2128570003d410'

        for entry in entries:
            url = entry.wp_url.split('.com')[0] + '.com/xmlrpc.php'
            client = Client(url, user, password)
            wpost = client.call(posts.GetPost(entry.wp_id))

            for t in wpost.terms:
                if t.name == 'Portada':
                    print t.id
                    wpost.terms.remove(t)
                    break

            client.call(posts.EditPost(entry.wp_id, wpost))
            logger.info("inserted cannonical in %s" % entry.wp_url)
