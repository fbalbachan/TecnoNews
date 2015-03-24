# -*- coding: utf-8 -*-

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods import taxonomies
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *
from src.utils.configProvider import ConfigProvider
from src.utils.imgeProcessor import to_desired_size
import urllib
from wordpress_xmlrpc.compat import xmlrpc_client
import mimetypes
from src.utils.SvgToPng import to_png

logger = get_logger('tecnonews')


class BlogPublisher(object):

    def __init__(self):
        self.config = ConfigProvider()

    @staticmethod
    def check_and_remove_con_foto(client, wp_id):
        wpost = client.call(posts.GetPost(wp_id))
        print wpost.thumbnail
        if not wpost.thumbnail:
            cf = None
            # TODO: use taxonomies insted of checking the name
            for t in wpost.terms:
                if t.name == 'z con foto':
                    print t.name
                    # we are in the case where we upload a photo asign it and
                    # some how thumbnail is not setted so remove category 'z con foto
                    cf = t
            if cf:
                wpost.terms.remove(cf)
        client.call(posts.EditPost(wp_id, wpost))

    def process_image(self, client, entry, post_id):
        thumbnail = None
        if entry.image:
            image_data = self.get_data_upload_image(entry.image)
            image_data['post_id'] = post_id

            logger.info("image info %s" % image_data)

            response = client.call(media.UploadFile(image_data))
            logger.info("response after upload image %s " % response)
            thumbnail = int(response['id'])

            logger.info("thumbnail id:%s" % thumbnail)

        else:
            logger.info("doesnt have image")

        return thumbnail

    def get_category_instance(self, client, name):
        categories = client.call(taxonomies.GetTerms('category'))
        for cat in categories:
            if cat.name == name:
                return cat

    def special_catogory_insertion(self, client, entry, post, thumbnail):
        # Portada minimal logic
        logger.info("post.injected_count %s" % entry.injected_count)

        if thumbnail:
            post.thumbnail = thumbnail
        if hasattr(post, 'thumbnail') and isinstance(post.thumbnail, int):
            con_foto_instance = self.get_category_instance(client, "z con foto")
            post.terms.append(con_foto_instance)
            logger.info("z con foto")

        assert isinstance(entry.injected_count, int)

        if hasattr(post, 'thumbnail') \
                and isinstance(post.thumbnail, int) and entry.injected_count >= 2:
            destacada_instance = self.get_category_instance(client, "z destacada")
            post.terms.append(destacada_instance)
            logger.info("z destacada")

    def publish(self, entry, test=False):
        news_service = NewsEntriesService() if not test else NewsEntriesService('test')
        post = WordPressPost()
        post.title = entry.title
        post.content = entry.content

        host = self.select_category_to_publish(entry)
        logger.info("publishing into host %s" % host['url'])

        client = Client(host['url'], host['username'], host['password'])

        camelCategories = []

        for category in entry.categories:
            camelCategories.append(category[0].upper() + category[1:])

        post.terms_names = {
            'post_tag': entry.tags,
            'category': camelCategories
        }

        # Post new entry as draft
        wp_id = client.call(NewPost(post))

        # Get the just posted wordpress entry and save the url
        if wp_id:
            # get the draft post upload and associate image
            # set publish
            post = client.call(GetPost(wp_id))
            wp_url = post.link
            thumbnail = self.process_image(client, entry, wp_id)
            self.special_catogory_insertion(client=client,
                                            entry=entry,
                                            post=post,
                                            thumbnail=thumbnail)
            post.post_status = 'publish'
            client.call(posts.EditPost(wp_id, post))

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

    @staticmethod
    def get_data_upload_image(img):
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
            data['type'] = mimetypes.read_mime_types(filename_png) or mimetypes.guess_type(filename_png)[0]

        # Write into tmp_filepath a resized/ croped version of the image
        # TODO: Use the information about if it is a flag, person o map to optimizice
        # the resize/crop to the better image portion selection
        to_desired_size(tmp_filepath)
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
                if t.name == 'z destacada':
                    print t.id
                    wpost.terms.remove(t)
                    break

            client.call(posts.EditPost(entry.wp_id, wpost))
            logger.info("inserted cannonical in %s" % entry.wp_url)
