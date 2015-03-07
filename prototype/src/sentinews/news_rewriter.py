# -*- coding: utf-8 -*-

from src.model.sentilecto import Sentilecto
from src.sentinews.hyperlink_processor import HyperlinkProcessor
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.extension.textInserter import TextInserter
from src.rewrite.rewriter import Rewriter
from src.model.referent.referentRanker import ReferentRanker
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.utils.similarParagraph import SimilarParagraph
from src.utils.logger_utils import *
import re

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

    def _get_alt_text(self, im, h):
        im2 = [(x.split('/')[-1].split('.')[0], x) for x in im]

        res = {}
        for img, url in im2:
            try:
                x = re.search("\<img.*%s.*/>" % img, h).group(0)
                s = re.search("alt=\".*\" src=", x).group(0)
                s = s[s.find('"')+1:]
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
        blacklist = ['Commons-', 'Wikinews-logo', 'Flag_of_None', 'Red_pog',
                     'Wikisource-logo', 'Red_pog', 'Estany', 'Flag_of_Egypt',
                     'Ice_hockey_pictogram', 'Spanish Language Wiki.svg',
                     'Kit right arm blueshoulders.png', 'Tetragrammaton']

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
        # FIXME: analysis.text is str insted of unicode!!
        analysis = self._analyze(self.original_entry.content)
        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()

        # Generating content
        analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()
        sp = SimilarParagraph(analysis=analysis, other_versions=self.rewritten_entry.other_versions)
        analysis["generated_content_other_sources"] = sp.get_generated_content()

        wikiinfo = analysis["generated_content_wiki"]
        paragraph_from_other_cover = analysis["generated_content_other_sources"]
        ranking = analysis["referent_ranking"]

        # Insert new content
        text_inserter = TextInserter(analysis)
        self.rewritten_entry.content = text_inserter.get()

        analysis = self._analyze(self.rewritten_entry.content)
        rewriter = Rewriter(analysis['paragraph'])
        self.rewritten_entry.content = rewriter.rewrite()

        analysis = self._analyze(self.rewritten_entry.content)
        hyperlink_processor = HyperlinkProcessor(analysis)
        self.rewritten_entry.content = hyperlink_processor.get_text_with_hyperlinks()

        if wikiinfo and filter(lambda (referent, score): referent == wikiinfo[0][0] and score > 1., ranking):
            logger.info("WIKIINFO: %s", str(wikiinfo))
            logger.info("Searching for %s " % wikiinfo[0][2])
            entry_image = self.get_main_image_url(wikiinfo[0][2])
            if entry_image:
                self.rewritten_entry.image = entry_image
                logger.info("Url selected %s" % self.rewritten_entry.image['url'])
            else:
                logger.info("None image selected")
        else:
            logger.info("NO REFERENT SCORE > 1")

        self.post_process()

        # self.rewritten_entry.content += """[eyesonly logged="in"] wikiinfo: <br/>""" + str(wikiinfo) \
        #                                  + " other cover: <br/>" + str(paragraph_from_other_cover)  + "[/eyesonly]"
        # print "------------"
        # print wikiinfo
        # print "------------"

    def publish(self):
        publisher = BlogPublisher()
        return publisher.publish(self.rewritten_entry)

    def _analyze(self, text):
        return Sentilecto().analyze(text)

    def post_process(self):
        content = ''

        for paragraph in self.rewritten_entry.content.split('\n'):
            if len(paragraph) > 0:
                content += '<p>' + paragraph[0].upper() + paragraph[1:] + '</p>'

        self.rewritten_entry.content = content