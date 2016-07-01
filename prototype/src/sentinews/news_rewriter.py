# -*- coding: utf-8 -*-

import re
import traceback
import urllib

from src.model.sentilecto import Sentilecto
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.extension.textInserter import TextInserter
from src.rewrite.rewriter import Rewriter
from src.rewrite.globalRewriter import GlobalRewriter
from src.model.referent.referentRanker import ReferentRanker
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.utils.similarParagraph import SimilarParagraph
from src.utils.logger_utils import *
from src.sentinews.hyperlink_processor import HyperlinkProcessor

from src.utils.webOutputUtils import WebOutputUtils

from src.utils.sanitizer import Sanitizer
from src.utils.textSummarizer import TextSummarizer

logger = get_logger('tecnonews')
debug_mode = True


class NewsRewriter(object):
    ''' Main class that contains all information
        about the original news article and
        the rewritten result.
        Ties the crawler, the rewrite strategies and
        the publisher. '''

    def __init__(self, original_entry):
        self.original_entry = original_entry
        self.rewritten_entry = NewsEntry(original_entry.title,
                                         original_entry.content,
                                         original_entry.tags,
                                         original_entry.source,
                                         categories=original_entry.categories,
                                         related=original_entry.related,
                                         versions=original_entry.versions)
        self.injected_count = 0
        self.to_insert_canonical = []
        self.config = ConfigProvider()
        self.sanitizer = Sanitizer()

    def _get_alt_text(self, im, h):
        if debug_mode: logger.info("--> NEWS_REWRITER._get_alt_text()")

        im2 = [(x.split('/')[-1].split('.')[0], x) for x in im]

        res = {}
        for img, url in im2:
            try:
                x = re.search("\<img.*%s.*/>" % img, h).group(0)
                s = re.search("alt=\".*\" src=", x).group(0)
                s = s[s.find('"') + 1:]
                s = s[:s.find('"')]
                res[url] = s if len(s) > 0 else img
            except:
                res[url] = url

        if debug_mode: logger.info("<-- _get_alt_text >> result: [%s]" % (res.values()[0:2] if len(res) > 2 else ""))
        return res

    def get_main_image_url(self, wikipage):
        # TODO Rewrite this
        # TODO Extract this to a class

        img_alts = self._get_alt_text(wikipage.images, wikipage.html())
        images_urls = img_alts.keys()

        title_words = wikipage.original_title.lower().split()
        logger.info("search_string %s " % title_words)

        images_urls = self.pre_filter_images_urls(images_urls)

        candidate_urls = []
        for word in title_words:
            if len(word) < 4:
                # ignore short words
                continue

            for url in images_urls:
                if word in url.lower():
                    if url not in candidate_urls:
                        candidate_urls.append(url)

        logger.info("results %s " % candidate_urls)

        for url in candidate_urls:
            # ie we choose url if it is a Flag (ie have the flag word in it)
            if 'logo' in url:
                candidate_urls = [url]
                break
            elif 'Flag' in url:
                candidate_urls = [url]
                break

        logger.info("results after %s " % candidate_urls)

        if candidate_urls:
            selected_image = candidate_urls[0]
        else:
            # TODO Re think this default criteria
            # we didn't get a candidate just use the first one
            logger.info("Selection first image of the results because no criteria")
            if len(images_urls) > 0:
                selected_image = images_urls[0]
            else:
                selected_image = None

        image_info_dict = None
        if selected_image:
            logger.info("IMAGE URL: %s", selected_image)
            logger.info("IMAGE alt text: %s ", img_alts[selected_image])

            title = img_alts[selected_image]
            url = selected_image
            description = img_alts[selected_image]
            image_info_dict = dict(title=title, url=url, description=description)

        return image_info_dict

    @staticmethod
    def pre_filter_images_urls(images_urls):

        # TODO: make a resource with this info
        blacklist = \
            [
                'Commons-', 'Wikispecies-logo', 'Wiktionary-logo-es', 'Wikinews-logo', 'None', 'Spanish_Wikiquote.SVG', 'P_vip.svg',
                'Globe-with-clock.svg', 'Yes_check.svg', 'Red_pog', 'Wikisource-logo', 'Falta imagen', 'Estany', 'Flag_of_Egypt',
                'Ice_hockey_pictogram', 'Firmado pero no ratificado.', 'Spanish Language Wiki.svg',
                'Kit right arm blueshoulders.png', 'Tetragrammaton', 'signature', 'Signature', 'sig.',
                'LinkedInLogo', 'culo_bueno', 'Check_mark', '.tif', 'svg', '.ogg', '.ogv', '.gif', '.webm'
            ]

        filtered_urls = [url for url in images_urls
                         if not any(black_string in url for black_string in blacklist)]

        return filtered_urls

    def rewrite_title(self):
        analysis = self._analyze(self.original_entry.title)
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.title = rewriter.rewrite()
        self.rewritten_entry.title.replace('\n', ' ').replace('\t', ' ')
        self.rewritten_entry.title = self.sanitizer.post_process(self.rewritten_entry.title)


    def generate_entity_table(self, analysis):
        entity_table = ''


        sentences = analysis["paragraph"].sentences
        text_entities = []
        for sentence in sentences:
            for clause in sentence.clauses:
                clause_entities = clause.entities + clause.tacit_entities()

                clause_entities = filter(lambda entity: not entity.has_attr("implicit") and not entity.has_attr("impersonal"), clause_entities)

                clause_entities = filter(lambda entity: entity.is_maximal_regarding(clause_entities), clause_entities)

                text_entities.extend(clause_entities)
                if clause.relative_entity:
                    text_entities += [clause.relative_entity]

        output_utils = WebOutputUtils(None)
        if text_entities:
            referents_data = output_utils.get_referents_data(text_entities)
            i=0
            entity_table +='\n <u>Entidades mas mencionadas en la noticia:</u>'
            entity_table += '\n<table id="global_entities" border="1"><tr><th align="center">Id</th><th align="center">Entity</th><th align="center">Positive</th><th align="center">Negative</th><th align="center">Named-Entity</th><th align="center">Total occurrences</th><th align="center">Occurrences (appearances)</th></tr>'

            for referent_data in referents_data:

                if i > 9:
                    break

                appearing = {}
                for a_reference in referent_data['refs']:
                    a_reference = output_utils.e_name(a_reference)
                    if a_reference in appearing:
                        appearing[a_reference]+=1
                    else:
                        appearing[a_reference]=1

                unique_str = ""
                for unique_elem in appearing.iterkeys():
                    unique_str+=' ' + unique_elem+': '+output_utils.e_name(appearing[unique_elem])+','

                unique_str = unique_str[:-1]


                i+=1
                occurrences = len(referent_data['refs'])

                entity_table += '<tr>'
                entity_table += '<td align="center" width=30>' + str(i) + '</td>'
                entity_table += '<td align="center" title="' + output_utils.entity_tooltip(referent_data['re']) + '">' + referent_data['rn'] + '</td>'
                entity_table += '<td align="center" title="' + output_utils.e_sv_pos_ev(referent_data['refs']) + '" width=100>' + str(referent_data['pos']) + '</td>'
                entity_table += '<td align="center" title="' + output_utils.e_sv_neg_ev(referent_data['refs']) + '" width=100>' + str(referent_data['neg']) + '</td>'
                entity_table += '<td align="center" width=100>' + referent_data['sc'] + '</td>'
                entity_table += '<td align="center" width=100>' + str(occurrences) + '</td>'
                entity_table += '<td align="center" width=100>' + unique_str + '</td>'
                entity_table += '</tr>'

            entity_table += '</table>\n'

        return entity_table

    def rewrite_raconto(self):
        months = {
                    "01":u"enero",
                    "02":u"febrero",
                    "03":u"marzo",
                    "04":u"abril",
                    "05":u"mayo",
                    "06":u"junio",
                    "07":u"julio",
                    "08":u"agosto",
                    "09":u"septiembre",
                    "10":u"octubre",
                    "11":u"noviembre",
                    "12":u"diciembre",
                }
        days = {
                    "0":u"lunes",
                    "1":u"martes",
                    "2":u"miércoles",
                    "3":u"jueves",
                    "4":u"viernes",
                    "5":u"sábado",
                    "6":u"domingo",
        }

        intro = None
        if self.original_entry.raconto_date is not None:
            date = unicode(self.original_entry.raconto_date).split()[0]
            weekday = unicode(self.original_entry.raconto_date.weekday())
            date_numbers = date.split('-')

            if len(date_numbers) == 3:
                intro = u"El " + days[weekday] + u" " + date_numbers[2] + u" de " + months[date_numbers[1]] + u" " + self.original_entry.raconto_content
                intro = intro.encode("utf-8")
        if intro is None:
            intro = self.original_entry.raconto_content.encode("utf-8")

        return intro

    def rewrite_content(self):
        # TODO: Check every step catch exceptions and return OK|Fail
        # FIXME: analysis.text is str instead of unicode!!
        analysis = self._analyze(self.original_entry.content)

        logger.info("Trying summarization")
        try:
            self.original_entry.summary = TextSummarizer(analysis).summarize()
        except:
            logger.info("Summarization FAILED")
            pass

        applied_global = False
        try:
            global_text = GlobalRewriter(analysis["paragraph"]).rewrite()
            analysis = self._analyze(global_text)
            applied_global = (global_text != self.original_entry.content)
            #print "APPLIED GLOBAL"
            #print applied_global
        except:
            pass
        #analysis = self._analyze(GlobalRewriter(analysis["paragraph"]).rewrite())

        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()

        # Generating content
        analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()
        sp = SimilarParagraph(analysis=analysis, other_versions=self.rewritten_entry.other_versions)
        analysis["generated_content_other_sources"] = sp.get_generated_content()

        dated_raconto = self.rewrite_raconto
        if dated_raconto is not None:
            logger.info(type(dated_raconto))
            raconto_analysis = self._analyze(dated_raconto)
            rewriter = Rewriter(raconto_analysis['paragraph'])
            analysis["raconto_content"] = rewriter.rewrite(raconto=True)

        if not self.config.get('instance', 'id') == 'Test':
            self.to_insert_canonical = self.rewritten_entry.other_versions[:2]

        wikiinfo = analysis["generated_content_wiki"]
        paragraph_from_other_cover = analysis["generated_content_other_sources"]
        ranking = analysis["referent_ranking"]

        self.add_tags_from_ranking(analysis["referent_ranking"])

        # Insert new content
        text_inserter = TextInserter(analysis)
        self.injected_count, self.rewritten_entry.content = text_inserter.get()
        logger.info("Injected Count %s" % self.injected_count)

        self.rewritten_entry.injected_count = self.injected_count

        analysis = self._analyze(self.rewritten_entry.content)

        #TOKEN COUNT
        token_count = 0
        for a_sentence in analysis["paragraph"].sentences:
        	token_count += len(a_sentence.parse_node.leaves())

        rewriter = Rewriter(analysis['paragraph'], applied_global_strategies=applied_global)
        self.rewritten_entry.content = rewriter.rewrite()

        # Disable hyperlink insert until we fix some problems
        # TODO: Fix it
        # analysis = self._analyze(self.rewritten_entry.content)
        # hyperlink_processor = HyperlinkProcessor(analysis)
        # self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()
        #---------------------PRUEBA REACTIVACION PARA INTERNACIONALES-----------
        #if u"tecnología" not in self.original_entry.categories and u"estilo vida" not in self.original_entry.categories and u"propiedades" not in self.original_entry.categories:
        #    if u"internacionales" in self.original_entry.categories:
        #        analysis = self._analyze(self.rewritten_entry.content)
        #        hyperlink_processor = HyperlinkProcessor(analysis)
        #        self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()
        #-----------------------FIN PRUEBA INTERNACIONALES----------------------
        self.rewritten_entry.content = self.sanitizer.post_process(self.rewritten_entry.content)

        #------ALEXIS--------SENTIMENT SCORE
        logger.info("SENTIMENTSCORE")
        paragraph = analysis["paragraph"]
        sentiment_summary = analysis["summary"]
        #sentiment_score_text = "(+%.2f%%,-%.2f%%)" % (sentiment_summary[paragraph]['positive'], sentiment_summary[paragraph]['negative'])
        #self.rewritten_entry.content += "\n<b><u>Sentiment score (sentiment scale at the bottom of page): " + sentiment_score_text + "</u></b>\n"
        wording_result = ""

        positive_score = float(sentiment_summary[paragraph]['positive'])
        negative_score = abs(float(sentiment_summary[paragraph]['negative']))
        neutral_score = 0
        if positive_score == 0 and negative_score == 0:
            neutral_score = 1
        elif abs(positive_score-negative_score) < 5:
            neutral_score = 1
            positive_score = 0
            negative_score = 0
        elif positive_score < 10 and negative_score < 10:
            neutral_score = 1
            positive_score = 0
            negative_score = 0

        positive_score /= 100
        negative_score /= 100
        if positive_score > negative_score:
            wording_result = "POSITIVE"
        elif positive_score < negative_score:
            wording_result = "NEGATIVE"
        else:
            wording_result = "NEUTRAL"

        if max(positive_score, negative_score) >= 0.80:
            wording_result = "VERY " + wording_result
        elif max(positive_score, negative_score) < 0.35 and max(positive_score, negative_score) >= 0.10:
            wording_result = "SLIGHTLY " + wording_result

        self.original_entry.sentiment = wording_result
        self.original_entry.countries = []
        self.original_entry.cities = []

        #self.rewritten_entry.content += "\n<b><u>Sentiment score: " + wording_result + "</u></b>\n"

        #------ALEXIS--------COUNTRIES
        #logger.info("COUNTRIES")
        #entity_places = []
        #for an_entity in self.original_entry.entities:
        #    if an_entity["semantic"] == "place":
        #        entity_places.append(an_entity["name"])
        #        self.rewritten_entry.content += an_entity["name"]+" "


        #entity_places = []
        entity_countries = {}
        entity_cities = {}
        try:
            import socket,json
            sock = socket.socket()
            sock.settimeout(20)
            sock.connect(("85.10.210.172", 8081))
            sock.recv(1024)

            logger.info("COUNTRIES")

            for an_entity in self.original_entry.entities:
                if an_entity["semantic"] == "place":
                    #entity_places.append(an_entity["name"]
                    sock.send(an_entity["name"].replace("_"," ")+"\n")
                    a_response = json.loads(sock.recv(1024))
                    if a_response[0] != "Unknown":
                        if a_response[0] in entity_countries:
                            entity_countries[a_response[0]] += 1
                        else:
                            entity_countries[a_response[0]] = 1
                        #entity_places.append(a_response[0])
                    if a_response[1] != "Unknown":
                        if a_response[1] in entity_cities:
                            entity_cities[a_response[1]] += 1
                        else:
                            entity_cities[a_response[1]] = 1
                        #entity_places.append(a_response[1])
        except Exception as e:
            logger.error("COUNTRIES ERROR: %s" % e.message)
            logger.error("COUNTRIES ERROR: \n%s" % traceback.format_exc())

        #if len(entity_places) > 0:
        #    self.rewritten_entry.content += "Paises: "
        #    for a_place in entity_places:
        #        self.rewritten_entry.content += a_place.encode('utf-8') + ", "
        #    self.rewritten_entry.content = self.rewritten_entry.content[:-2]
        #    self.rewritten_entry.content += "."


        if len(entity_countries) > 0:
            #self.rewritten_entry.content += "<b><u>Countries:</u> "
            for a_country, a_count in sorted(entity_countries.iteritems(), key=lambda (k,v): (v,k),reverse=True):
                #self.rewritten_entry.content += a_country.encode('utf-8').title() + ", "
                self.original_entry.countries.append(a_country.encode('utf-8'))

            #self.rewritten_entry.content = self.rewritten_entry.content[:-2]
            #self.rewritten_entry.content += "</b>\n"


        if len(entity_cities) > 0:
            #self.rewritten_entry.content += "<b><u>Cities:</u> "
            for a_city, a_count in sorted(entity_cities.iteritems(), key=lambda (k,v): (v,k),reverse=True):
                #self.rewritten_entry.content += a_city.encode('utf-8').title() + ", "
                self.original_entry.cities.append(a_city.encode('utf-8'))
            #self.rewritten_entry.content = self.rewritten_entry.content[:-2]
            #self.rewritten_entry.content += "</b>\n"



        self.rewritten_entry.cities = self.original_entry.cities
        self.rewritten_entry.countries = self.original_entry.countries
        self.rewritten_entry.sentiment = self.original_entry.sentiment
        self.rewritten_entry.entity_table = self.generate_entity_table(analysis)
        self.rewritten_entry.token_count = token_count


        #ENTITY TABLE
        #self.rewritten_entry.content += self.generate_entity_table(analysis)

        if wikiinfo and filter(lambda (referent, score): referent == wikiinfo[0][0] and score > 1., ranking):
            # logger.info("WIKIINFO: %s", str(wikiinfo))
            # logger.info("Searching for %s " % wikiinfo[0][2])
            wikipedia_page = wikiinfo[0][2]
            entry_image = self.get_main_image_url(wikipedia_page)

            if entry_image:
                self.rewritten_entry.content = self.add_image_caption(entry_image, self.rewritten_entry.content)
                self.rewritten_entry.image = entry_image
                logger.info("Url selected %s" % self.rewritten_entry.image['url'])

            else:
                logger.info("No image selected")

        else:
            logger.info("NO REFERENT SCORE > 1")

        # Re try to find an image with entity from title
        if not self.rewritten_entry.image or not self.rewritten_entry.image['url']:
            logger.info("trying from title")
            # If we fail to select an image from text try with title entities
            analysis = self._analyze(self.original_entry.title)
            analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()
            analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()
            ranking = analysis["referent_ranking"]
            wikiinfo = analysis["generated_content_wiki"]

            if wikiinfo and filter(lambda (referent, score): referent == wikiinfo[0][0] and score > 1., ranking):
                # logger.info("WIKIINFO: %s", str(wikiinfo))
                # logger.info("Searching for %s " % wikiinfo[0][2])
                wikipedia_page = wikiinfo[0][2]
                entry_image = self.get_main_image_url(wikipedia_page)

                if entry_image:
                    self.rewritten_entry.content = self.add_image_caption(entry_image, self.rewritten_entry.content)
                    self.rewritten_entry.image = entry_image
                    logger.info("From title Url selected %s" % self.rewritten_entry.image['url'])
                else:
                    logger.info("No image selected from title")

        self.post_process()



    def publish(self):
        publisher = BlogPublisher()
        wp_id, wp_url, host_id, image_url = publisher.publish(self.rewritten_entry)
        if host_id == u"entretenimiento_bit":
            publisher.insert_canonical(self.to_insert_canonical, wp_url)
            publisher.remove_from_portada(self.to_insert_canonical)
        return wp_id, wp_url, host_id, image_url

    def _analyze(self, text):
        return Sentilecto.analyze(text)

    #20160129 - Daniel Cantarin
    #Captions are usually got from wikipedia, and are often urlencoded
    #file names. This function applies common filters in order to get
    #a more human friendly caption.
    def _sanitize_caption(self, caption):

        #if not isinstance(caption, basestring):
        #    return caption

        ret  = caption
        # 1) Restore URL escaped characters.
        try :
            #ALEXIS: Encodeo a UTF-8 PORQUE LOS URL ENCODINGS (%%) DEPENDEN DEL ENCODING FUENTE (WINDOWS-1xxx != UTF-8)
            ret = ret.encode('utf-8')

            #DECODEO PORCENTAJES
            ret  = urllib.unquote(ret)

            #VUELVO A CONVERTIR A UNICODE PORQUE ERA LO QUE ME VINO
            ret = ret.decode('utf-8')
        except :
            pass

        # 2) Dealing with encodings.
        # try :
        #     ret = ret.decode("utf8")
        # except :
        #    pass

        # 3) Remove common file extensions for images.
        exts = [".jpg", ".JPG", ".svg", ".SVG", ".png", ".PNG", ".gif", ".GIF"]
        for ext in exts:
            ret = ret.replace(ext, "")

        # 4) Change underscores for blank spaces.
        ret  = ret.replace("_"," ")

        return ret


    def add_image_caption(self, image_data, rewritten_content):
        if debug_mode: logger.info("--> NEWS_REWRITER.add_image_caption()")

        rewritten_content_with_caption = rewritten_content
        try:
            caption = image_data['description']
            if isinstance(rewritten_content, unicode):
                logger.info("Rewritten entry content is unicode")
                if not isinstance(caption, unicode):
                    logger.info('Caption is UTF-8')
                    caption = unicode(caption,"utf-8")
                caption = self._sanitize_caption(caption)
                logger.info(u'Image Caption: %s' % caption)
                rewritten_content_with_caption = u'<p><small>Foto: Wikipedia - %s</small></p> %s' % (caption, rewritten_content)
            else:
                logger.info("Rewritten entry content is UTF-8")
                if isinstance(caption, unicode):
                    logger.info('Caption is UNICODE')
                    caption = caption.encode("utf-8")
                caption = self._sanitize_caption(caption)
                logger.info('Image Caption: %s' % caption)
                rewritten_content_with_caption =  '<p><small>Foto: Wikipedia - %s</small></p> %s' % (caption, rewritten_content)

        except Exception as e:
            caption = image_data['description'] if 'description' in image_data else "NO CAPTION"
            if isinstance(caption, unicode):
                logger.info(u'Image Caption error 1! Caption: %s' % caption)
            else:
                logger.info('Image Caption error 1! Caption: %s' % caption)

            logger.error(traceback.format_exc())

        if debug_mode: logger.info("<-- NEWS_REWRITER.add_image_caption >> result: %s" % (caption if caption else "NO CAPTION"))
        return rewritten_content_with_caption

    def add_tags_from_ranking(self, ranking):
        new_tags_list = [r[0].name() for r in ranking]
        logger.info("Tags in Ranking %s" % new_tags_list)
        if not new_tags_list:
            print "Empty tags to add"

        base_tags = self.rewritten_entry.tags
        if not base_tags:
            base_tags = []
        # avoid error if is a set instead of a list
        # TODO: put asserts in news entry to make this an assert
        if not isinstance(base_tags, list):
            base_tags = list(base_tags)

        logger.info("base tags %s " % base_tags)

        for tag in new_tags_list:
            tag_clean = re.sub('_', ' ', tag)
            tag_clen_utf = tag_clean.decode('utf-8')
            if tag_clen_utf not in base_tags:
                base_tags.append(tag_clean)

            if len(base_tags) >= 15:
                break

        logger.info("new tags %s" % base_tags)
        new_tags = list(set(base_tags))

        self.rewritten_entry.tags = new_tags

    def post_process(self):
        import traceback
        from src.utils.unicodeTools import safe_unicode
        pre_content = safe_unicode(self.rewritten_entry.content)
        content = u''

        for paragraph in pre_content.split(u'\n'):
            if len(paragraph) > 0:
                # patch to clean wrong formatted paragraphs
                if paragraph[0] in [u',', u'.']:
                    paragraph = paragraph[1:].strip()

                content += u'<p>' + paragraph[0].upper() + paragraph[1:] + u'</p>'

        try:
            logger.info("Is content unicode %s" % isinstance(content, unicode))
            # content = safe_unicode(content)
            content = re.sub(r' +',  u' ', content)

        except Exception as e:
                logger.error("Couldn't clean multiple spaces")
                logger.error("%s" % e.message)
                logger.error(traceback.format_exc())

        self.rewritten_entry.content = content
