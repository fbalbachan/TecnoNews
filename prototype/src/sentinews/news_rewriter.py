# -*- coding: utf-8 -*-

import re

from src.model.sentilecto import Sentilecto
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.extension.textInserter import TextInserter
from src.rewrite.rewriter import Rewriter
from src.model.referent.referentRanker import ReferentRanker
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.utils.similarParagraph import SimilarParagraph
from src.utils.logger_utils import *

logger = get_logger('tecnonews')


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

    def _get_alt_text(self, im, h):
        im2 = [(x.split('/')[-1].split('.')[0], x) for x in im]

        res = {}
        for img, url in im2:
            try:
                x = re.search("\<img.*%s.*/>" % img, h).group(0)
                s = re.search("alt=\".*\" src=", x).group(0)
                s = s[s.find('"') + 1:]
                s = s[:s.find('"')]
                res[url] = s
            except:
                res[url] = url
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
        blacklist = ['Commons-', 'Wikispecies-logo', 'Wiktionary-logo-es', 'Wikinews-logo', 'None', 'Spanish_Wikiquote.SVG', 'P_vip.svg', 'Globe-with-clock.svg', 'Yes_check.svg', 'Red_pog',
                     'Wikisource-logo', 'Falta imagen', 'Estany', 'Flag_of_Egypt',
                     'Ice_hockey_pictogram', 'Firmado pero no ratificado.', 'Spanish Language Wiki.svg',
                      'Kit right arm blueshoulders.png', 'Tetragrammaton', 'signature', 'Signature', 'sig.',
                      'LinkedInLogo', 'culo_bueno', 'Check_mark', 'svg']

        filtered_urls = [url for url in images_urls
                         if not any(black_string in url for black_string in blacklist)]

        return filtered_urls

    def rewrite_title(self):
        analysis = self._analyze(self.original_entry.title)
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.title = rewriter.rewrite()
        self.rewritten_entry.title = self.original_entry.title

    def rewrite_content(self):
        # TODO: Check every step catch exceptions and return OK|Fail
        # FIXME: analysis.text is str instead of unicode!!
        analysis = self._analyze(self.original_entry.content)
        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()

        # Generating content
        analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()
        sp = SimilarParagraph(analysis=analysis, other_versions=self.rewritten_entry.other_versions)
        analysis["generated_content_other_sources"] = sp.get_generated_content()

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
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.content = rewriter.rewrite()

        # Disable hyperlink insert until we fix some problems
        # TODO: Fix it
        # analysis = self._analyze(self.rewritten_entry.content)
        # hyperlink_processor = HyperlinkProcessor(analysis)
        # self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()

        if wikiinfo and filter(lambda (referent, score): referent == wikiinfo[0][0] and score > 1., ranking):
            # logger.info("WIKIINFO: %s", str(wikiinfo))
            # logger.info("Searching for %s " % wikiinfo[0][2])
            wikipedia_page = wikiinfo[0][2]
            entry_image = self.get_main_image_url(wikipedia_page)
            if entry_image:
                self.rewritten_entry.image = entry_image
                logger.info("Url selected %s" % self.rewritten_entry.image['url'])
            else:
                logger.info("None image selected")
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
                    self.rewritten_entry.image = entry_image
                    logger.info("From title Url selected %s" % self.rewritten_entry.image['url'])
                else:
                    logger.info("None image selected from title")

        self.post_process()

    def publish(self):
        publisher = BlogPublisher()
        wp_id, wp_url = publisher.publish(self.rewritten_entry)
        publisher.insert_canonical(self.to_insert_canonical, wp_url)
        publisher.remove_from_portada(self.to_insert_canonical)
        return wp_id, wp_url

    def _analyze(self, text):
        return Sentilecto.analyze(text)

    def add_tags_from_ranking(self, ranking):
        new_tags_list = [r[0].name() for r in ranking]
        logger.info("Tags in Ranking %s" % new_tags_list)
        if not new_tags_list:
            print "Empty tags to add"

        base_tags = self.rewritten_entry.tags
        if not base_tags:
            base_tags = []

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
                #patch to clean wrong formated paragraphs
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