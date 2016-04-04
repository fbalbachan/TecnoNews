# -*- coding: utf-8 -*-

import wordpress_xmlrpc
import urllib
import mimetypes
import traceback

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods import taxonomies
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.logger_utils import *
from src.utils.configProvider import ConfigProvider
from src.utils.imgeProcessor import to_desired_size, add_background
from wordpress_xmlrpc.compat import xmlrpc_client
from src.utils.SvgToPng import to_png
from src.utils.stringUtils import has_type_encoding
from src.sentinews.hyperlink_processor import HyperlinkProcessor

import datetime

from src.services.mongodb.hosts_service import HostsService
from bson.objectid import ObjectId

#from src.utils.csvwrapper import unicode_csv_reader

logger = get_logger('tecnonews')
debug_mode = True


class BlogPublisher(object):

    def __init__(self):
        self.config = ConfigProvider()
        #countries_file = self.config.get("resources", "countries")
        #countries_reader = unicode_csv_reader(open(countries_file, 'r'), first_line_is_header=False, delimiter=',')
        #self.countries_list = [unicode(country[0].lower(), 'utf-8') for country in countries_reader]

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
        if debug_mode: logger.info("--> BLOG_PUBLISHER.process_image()")
        thumbnail = None
        image_url = None
        if entry.image:
            image_data = self.get_data_upload_image(entry.image)
            image_data['post_id'] = post_id

            logger.info("image info %s" % image_data)

            response = client.call(media.UploadFile(image_data))
            logger.info("response after upload image %s " % response)

            if response != None and 'url' in response:
                image_url = response['url']

            thumbnail = int(response['id'])

            logger.info("thumbnail id:%s" % thumbnail)

        else:
            logger.info("doesnt have image")

        if debug_mode: logger.info("<-- BLOG_PUBLISHER.process_image() >> thumbnail id: %s" % (thumbnail))
        return thumbnail, image_url

    def get_category_instance(self, client, name):
        categories = client.call(taxonomies.GetTerms('category'))
        for cat in categories:
            if cat.name == name:
                return cat

    def special_catogory_insertion(self, client, entry, post):
        # Portada minimal logic
        logger.info("post.injected_count %s" % entry.injected_count)
        has_valid_thubmnail_id = False

        if hasattr(post, 'thumbnail'):
            if post.thumbnail:
                has_valid_thubmnail_id = True

        if has_valid_thubmnail_id:
            con_foto_instance = self.get_category_instance(client, "z con foto")
            if not isinstance(con_foto_instance,
                              wordpress_xmlrpc.wordpress.WordPressTerm):
                logger.error("Category 'z con foto' isn't there, not applying that category")

            else:

                post.terms.append(con_foto_instance)
                logger.info("z con foto")

        assert isinstance(entry.injected_count, int)

        if has_valid_thubmnail_id and entry.injected_count >= 2:
            destacada_instance = self.get_category_instance(client, "z destacada")

            if not isinstance(destacada_instance,
                              wordpress_xmlrpc.wordpress.WordPressTerm):
                logger.error("Category 'z destacada' isn't there, not applying that category")
            else:
                post.terms.append(destacada_instance)
                logger.info("z destacada")





    def add_countries(self, entry, limit=None):
        if limit is not None:
            country_list = entry.countries[:limit]
        else:
            country_list = entry.countries

        if len(country_list) > 0:
            entry.content += "<p class='country'><b><u>Countries:</u> "
            for a_country in country_list:
                entry.content += a_country.title() + ", "
            entry.content = entry.content[:-2]
            entry.content += "</b></p>"

    def add_cities(self, entry, limit=None):
        if limit is not None:
            city_list = entry.cities[:limit]
        else:
            city_list = entry.cities

        if len(city_list) > 0:
            entry.content += "<p class='city'><b><u>Cities:</u> "
            for a_city in city_list:
                entry.content += a_city.title() + ", "
            entry.content = entry.content[:-2]
            entry.content += "</b></p>"

    def add_sentiment(self, entry):
        if entry.sentiment:
            entry.content += "<p class='sentiment-score'><b><u>Sentiment score: " + entry.sentiment + "</u></b></p>"

    def add_entity_table(self, entry):
        if entry.entity_table:
            entry.content += entry.entity_table


    def add_related_news_tree(self, entry, news_service, show_source=True, show_link=True):
        post = entry
        if len(entry.versions) > 0:
            logger.info("Found several coverages: %s" % (str(entry.versions)))
            #Fuentes relevadas para esta noticia
            post.content += "<p class='history-tree'><b><u>La historia de esta noticia a partir de noticias previas: </u></b>"

            treeEntries = []
            added_entries_ids = []

            depth = 1
            entryDate = ""
            entry.versions = entry.versions[:3]

            try:
                entryDate = entry.published_date.strftime('%B %d, %Y')
            except:
                entryDate = ""

            if isinstance(entryDate, unicode):
                entryDate = entryDate.encode("utf-8")

            main_source = entry.source
            if isinstance(main_source, unicode):
                main_source = main_source.encode("utf-8")

            main_title = entry.title
            if isinstance(main_title, unicode):
                main_title = main_title.encode("utf-8")

            post.content += "<br>>"
            post.content += main_title

            for aRoot in reversed(entry.versions):
                treeEntries.append({'depth':depth, '_id': aRoot})


            while len(treeEntries) > 0:
                currentElement = treeEntries.pop()
                dbEntry = news_service.get_list({'_id':currentElement['_id']})


                if currentElement['_id'] in added_entries_ids:
                    continue

                added_entries_ids.append(currentElement['_id'])


                if len(dbEntry) > 0:
                    if dbEntry[0].wp_id != None and currentElement['depth'] < 5:
                        dbEntry[0].versions = dbEntry[0].versions[:3]
                        for anEntryId in reversed(dbEntry[0].versions):
                            treeEntries.append({'depth':currentElement['depth']+1, '_id': anEntryId})

                    tabs = " "
                    for aTab in range(currentElement['depth']):
                        tabs += ">>>>"

                    entryDate = ""
                    try:
                        entryDate = dbEntry[0].published_date.strftime('%B %d, %Y')
                    except:
                        entryDate = ""

                    post_url = dbEntry[0].wp_url
                    if isinstance(post_url, unicode):
                        post_url = post_url.encode("utf-8")

                    post_title = dbEntry[0].title
                    if isinstance(post_title, unicode):
                        post_title = post_title.encode("utf-8")

                    post_source = dbEntry[0].source
                    if isinstance(post_source, unicode):
                        post_source = post_source.encode("utf-8")

                    if dbEntry[0].wp_url != None and show_link:
                        if show_source:
                            post.content += "<br>" + tabs + ">" + "<a href=\"" +post_url+ "\">" + post_title + "</a>" + " - " +  entryDate + " (EntretenimientoBit)"
                        else:
                            post.content += "<br>" + tabs + ">" + "<a href=\"" +post_url+ "\">" + post_title + "</a>" + " - " +  entryDate
                    else:
                        if show_source:
                            post.content += "<br>" + tabs + ">" + post_title + " - " +  entryDate + " (" + post_source + ")"
                        else:
                            post.content += "<br>" + tabs + ">" + post_title + " - " +  entryDate

            post.content += "</p>"






    def publish(self, entry, test=False):
        if debug_mode: logger.info("--> BLOG_PUBLISHER.publish(title: %s)" % (entry.title if (entry and entry.title) else "NO TITLE"))


        if has_type_encoding(entry.content, str, 'UTF-8'):
            logger.info("Content is UTF8")
            pass # we expect it to be UTF-8
        if has_type_encoding(entry.content, unicode):
            logger.info("Content is UNICODE")
            entry.content = entry.content.encode("utf-8")


        news_service = NewsEntriesService()
        hosts_service = HostsService()

        #--PICK HOST AND CUSTOMIZE CONTENT--
        valid_host = False

        #Specific hosts:
        hosts = hosts_service.get_list({'categories': {'$in': entry.categories}, "enabled":True})
        hosts = sorted(hosts, key=lambda a_host: a_host["priority"] if "priority" in a_host else 10000, reverse=True)
        while not valid_host:
            if len(hosts) == 0:
                #Non specific hosts:
                hosts = hosts_service.get_list({'categories': {'$in': ["*"]}, "enabled":True})
                if len(hosts) == 0:
                    host = None         #No more hosts
                    valid_host = True   #Ends loop

            host = hosts.pop()


            #TODO Check limits => TEMP!
            if host['id'] == u"politica_bit":
                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=86400) #1 Day
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 5:
                    valid_host = True
                    host["password"] = u"MarioKempes" #TEMP
            elif host['id'] == u"alma_shopping":

                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 300:
                    valid_host = True
                    host["password"] = u"District93_Alma" #TEMP
                    entry.categories = [u"ARTICULOS"]

            elif host['id'] == u"properati":

                valid_country = False
                valid_countries = [ u'argentina', u'uruguay', u'chile', u'mexico', u'united states']
                for country in valid_countries :
                    if country in entry.countries :
                        valid_country = True
                        break

                if len(entry.countries) == 0:
                    valid_country = True

                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 150 and valid_country:
                    interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=86400) #1 Day
                    post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                    if post_count < 10:
                        valid_host = True
                        entry.categories = [u"Noticias"]
                        entry.tags = []

            elif host['id'] == u"femeninas":
                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})

                if post_count < 110:
                    interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=86400) #1 Day
                    if u'entretenimiento' in entry.categories :
                        post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'entretenimiento'})
                        if post_count < 2 :
                            valid_host = True

                    elif u'estilo vida' in entry.categories:
                        post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'estilo vida'})
                        if post_count < 5:
                            valid_host = True

                    if valid_host:
                        entry.categories = [u"uncategorized"]

            elif host['id'] == u"think_thank":
                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 1000:
                    interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=86400) #1 Day
                    post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                    if post_count < 40:
                        entry.categories = [u'--------CAMBIAR----------']
                        valid_host = True

            elif host['id'] == u"les_amis":

                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 285:
                    valid_host = True

            elif host['id'] == u"noticias_com":
                logger.info("Evaluating noticias.com...")
                # 20160203 - Daniel Cantarin
                # Added filter by country logic.
                valid_country = False
                valid_countries = [ u'peru', u'vatican city', u'bolivia', u'paraguay', u'uruguay', u'panama', u'honduras', u'nicaragua', u'el salvador', u'costa rica', u'mexico', u'colombia', u'ecuador', u'brazil', u'united states', u'argentina', u'venezuela', u'chile', u'china', u'japan', u'korea' ]
                for country in valid_countries :
                    if country in entry.countries :
                        valid_country = True
                        break

                logger.info("Valid countries: " + str(valid_country))
                if entry.image:
                    logger.info("Entry has image")

                interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=2592000) #1 Month
                post_count = news_service.get_count({'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id']})
                if post_count < 1800:
                    interval_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=86400) #1 Day

                    if u'policiales' in entry.categories and valid_country:
                        logger.info("Case: Noticias.com->Policiales")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'policiales'})

                        if post_count < 10:
                            entry.categories = [u'sucesos']
                            valid_host = True

                    if u'internacionales' in entry.categories and valid_country and entry.image:
                        logger.info("Case: Noticias.com->Internacionales")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'internacionales'})

                        if post_count < 10:
                            entry.categories = [u'sucesos']
                            valid_host = True

                    if u'deporte' in entry.categories and valid_country and entry.image:
                        logger.info("Case: Noticias.com->Deporte")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'deporte'})

                        if post_count < 6:
                            entry.categories = [u'deportes']
                            valid_host = True

                    if u'economía' in entry.categories and valid_country:
                        logger.info("Case: Noticias.com->Economía")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'economía'})

                        if post_count < 6:
                            entry.categories = [u'sucesos']
                            valid_host = True

                    if u'entretenimiento' in entry.categories :
                        logger.info("Case: Noticias.com->Entretenimiento")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'entretenimiento'})

                        if post_count < 40 :
                            entry.categories = [u'entretenimiento']
                            valid_host = True

                    if u'clima' in entry.categories and valid_country and entry.image:
                        logger.info("Case: Noticias.com->Clima")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'clima'})

                        if post_count < 6:
                            entry.categories = [u'sucesos']
                            valid_host = True

                    if u'estilo vida' in entry.categories:
                        logger.info("Case: Noticias.com->Estilo Vida")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'estilo vida'})

                        if post_count < 0:
                            entry.categories = [u'sociedad']
                            valid_host = True


                    if u'interés general' in entry.categories and valid_country:
                        logger.info("Case: Noticias.com->interés general")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'interés general'})

                        if post_count < 10:
                            entry.categories = [u'sociedad']
                            valid_host = True


                    if u'ciencia' in entry.categories:
                        logger.info("Case: Noticias.com->ciencia")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'ciencia'})

                        if post_count < 6:
                            entry.categories = [u'insólito']
                            valid_host = True


                    if u'tecnología' in entry.categories:
                        logger.info("Case: Noticias.com->tecnología")
                        post_count = news_service.get_count(
                            {'_id': {'$gte': ObjectId.from_datetime(interval_time)}, 'host_id': host['id'], 'categories': u'tecnología'})

                        if post_count < 20:
                            entry.categories = [u'sociedad']
                            valid_host = True


            else:
                valid_host = True #TEMP
                host["password"] = u"MarioKempes" #TEMP
                self.add_sentiment(entry)
                self.add_countries(entry)
                self.add_cities(entry)
                self.add_related_news_tree(entry, news_service)
                self.add_entity_table(entry)


        #--CREATE WP POST--
        post = WordPressPost()
        post.title = entry.title
        post.content = entry.content


        logger.info("publishing into host %s" % host['url'])

        client = Client(host['url'], host['username'], host['password'])

        camelCategories = []

        #logger.info("ALEXIS: categories: %s" % ', '.join(entry.categories))
        if u"belleza" in entry.categories:
            entry.categories = [u"belleza"]

        if u"propiedades" in entry.categories:
            entry.categories = [u"propiedades"]
            c                = ConfigProvider()
            path             = c.get("resources","resources_dir") + "/hyperlinks_propiedades.csv"
            post.content     = HyperlinkProcessor.apply_links_by_CSV(post.content, path)

        if u"tecnología" in entry.categories:
            entry.categories = [u"tecnología"]

        if u"turismo" in entry.categories:
            entry.categories = [u"turismo"]

        if u"estilo vida" in entry.categories:
            entry.categories = [u"estilo vida"]

#        if u"propiedades" in entry.categories:
#            entry.categories = [u"propiedades"]

        for category in entry.categories:
            camelCategories.append(category[0].upper() + category[1:])

        post.terms_names = {
            'post_tag': entry.tags,
            'category': camelCategories
        }

        #logger.info("ALEXIS entry.tags: %s" % ', '.join(entry.tags))

        # Post new entry as draft
        wp_id = client.call(NewPost(post))
        logger.info("wp_id response from newPost %s" % wp_id)

        # Get the just posted wordpress entry and save the url
        if wp_id:
            wp_id = int(wp_id)
            logger.info("wp_id %s" % wp_id)
            # get the draft post upload and associate image
            # set publish
            post = client.call(GetPost(wp_id))
            wp_url = post.link
            #logger.info("ALEXIS wpLink: %s" % wp_url)
            thumbnail, image_url = self.process_image(client, entry, wp_id)
            if thumbnail:
                post.thumbnail = thumbnail

            self.special_catogory_insertion(client=client,
                                            entry=entry,
                                            post=post)
            if host["draft"] == False:
                post.post_status = 'publish'
            self.insert_source_data(entry=entry, post=post)

            client.call(posts.EditPost(wp_id, post))

        else:
            logger.error("not wp_id %s" % wp_id)
            wp_url = ""
            image_url = None

        if debug_mode: logger.info("<-- BLOG_PUBLISHER.publish(wp_id: %s, wp_url: %s)" % (wp_id, wp_url))
        return wp_id, wp_url, host["id"], image_url

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

    def get_unique_host_to_publish(self):
        import json
        user_per_categories_file = self.config.get('publishing', 'unique_host_data')

        with open(user_per_categories_file) as f:
            unique_host = json.loads(f.read())
        return unique_host

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
        try:
            add_background(tmp_filepath)
        except Exception as e:
            logger.error("Error inserting background")
            logger.error("%s" % e.message)

        # read the binary file and let the XMLRPC library encode it into base64
        with open(tmp_filepath, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())

        return data

    def insert_canonical(self, entries, new_post_url):

        # don't insert canonical if we use the test
        instance_id = self.config.get('instance', 'id')
        if instance_id == 'Test':
            return

        # TODO: workaround this hardcoded data
        user = 'emmettbrown'
        password = 'MarioKempes'
        for entry in entries:
            if not entry.wp_url:
                logger.error(entry.title)
                logger.error(entry.wp_url)
                logger.error(entry.wp_id)
                logger.error("not inserting canonical")
                continue

            url = entry.wp_url.split('.com')[0] + '.com/xmlrpc.php'
            client = Client(url, user, password)
            try:
                wpost = client.call(posts.GetPost(entry.wp_id))
                wpost.custom_fields = [dict(key='my_canonical', value=new_post_url)]
                if wpost.thumbnail:
                    wpost.thumbnail = wpost.thumbnail['attachment_id']
                client.call(posts.EditPost(entry.wp_id, wpost))
                logger.info("inserted cannonical in %s" % entry.wp_url)
            except Exception as e:
                logger.error("Couldn't recover and update entry %s" % entry.wp_id)
                logger.error("%s" % e.message)

    def remove_from_portada(self, entries):
        # TODO: workaround this hardcoded data
        user = 'emmettbrown'
        password = 'MarioKempes'

        for entry in entries:
            try:
                if not entry.wp_url:
                    logger.error(entry.title)
                    logger.error(entry.wp_url)
                    logger.error(entry.wp_id)
                    logger.error("not inserting canonical")
                    continue

                url = entry.wp_url.split('.com')[0] + '.com/xmlrpc.php'
                client = Client(url, user, password)
                wpost = client.call(posts.GetPost(entry.wp_id))

                for t in wpost.terms:
                    if t.name == 'z destacada':
                        print t.id
                        wpost.terms.remove(t)
                        break

                if wpost.thumbnail:
                    wpost.thumbnail = wpost.thumbnail['attachment_id']
                client.call(posts.EditPost(entry.wp_id, wpost))
                logger.info("remove from portada in %s" % entry.wp_url)
            except Exception as e:
                logger.error("Couldn't remove from portada %s" % entry.wp_id)
                logger.error("%s" % e.message)

    def insert_source_data(self, entry, post):
        post.custom_fields.append(dict(key='source', value=entry.source))
