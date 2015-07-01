# -*- coding: utf-8 -*-

from src.services.mongodb.feeds_service import FeedService
from src.sentinews.crawler import Crawler
from src.sentinews.feeds import Feed
from src.services.mongodb.connector import MongoConnector
from datetime import datetime
from src.utils.logger_utils import get_crawler_logger
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.utils.configProvider import ConfigProvider

crawler_logger = get_crawler_logger()


class NewsCrawler(object):
    """ This class also builds and inserts into DB.
    DB structure:
      Table feed_sources: id and url of all feeds from where to read the news.
      Table original_news_entries: title, text and url of all news read.
    """
    def __init__(self):
        config = ConfigProvider()
        self.feeds_to_process = list(config.get("news_sources", "feeds_to_process").split(','))
        self.feed_service = FeedService()
        self._cursor_start()

    def _cursor_start(self):
        db = MongoConnector.get_instance()
        insert_feed_in_db = True

        if 'feeds' in db.collection_names():
            # if not zero insert_feed_in_db is False
            if db['feeds'].count():
                insert_feed_in_db = False

        if insert_feed_in_db:
            self.feed_service.save(Feed('cnn_spanish', 'http://cnnespanol.cnn.com/feed/',
                                        'cnn_parser.CNNParser', datetime.utcnow()))
            self.feed_service.save(Feed('euronews', 'http://feeds.feedburner.com/euronews/es/news?format=xml',
                                        'euronews_parser.EuroNewsParser', datetime.utcnow()))
            self.feed_service.save(Feed('elpais', 'http://ep00.epimg.net/rss/tags/ultimas_noticias.xml',
                                        'elpais_parser.ElPaisParser', datetime.utcnow()))
            self.feed_service.save(Feed('elpais_america', 'http://ep00.epimg.net/rss/elpais/portada_america.xml',
                                        'elpais_parser.ElPaisParser', datetime.utcnow()))
            self.feed_service.save(Feed('bbc_america', 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['america']))
            self.feed_service.save(Feed('bbc_internacional', 'http://www.bbc.co.uk/mundo/temas/internacional/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['america']))
            self.feed_service.save(Feed('bbc_economia', 'http://www.bbc.co.uk/mundo/temas/economia/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['economia']))
            self.feed_service.save(Feed('bbc_tecnologia', 'http://www.bbc.co.uk/mundo/temas/tecnologia/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['tecnologia']))
            self.feed_service.save(Feed('bbc_ciencia', 'http://www.bbc.co.uk/mundo/temas/ciencia/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['ciencia']))
            self.feed_service.save(Feed('bbc_salud', 'http://www.bbc.co.uk/mundo/temas/salud/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['salud']))
            self.feed_service.save(Feed('bbc_cultura', 'http://www.bbc.co.uk/mundo/temas/cultura/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['sociedad']))
            self.feed_service.save(Feed('bbc_deportes', 'http://www.bbc.co.uk/mundo/temas/deportes/index.xml',
                                        'bbc_parser.BBCParser', datetime.utcnow(), ['deportes']))
            self.feed_service.save(Feed('elmundo', 'http://www.elmundo.es/rss/portada.xml',
                                        'elmundo_parser.ElMundoParser', datetime.utcnow()))
            self.feed_service.save(Feed('abc', 'http://www.abc.es/rss/feeds/abc_ultima.xml',
                                        'abc_parser.ABCParser', datetime.utcnow()))
            self.feed_service.save(Feed('europa_press_internacional', 'http://www.europapress.es/rss/rss.aspx?ch=69',
                                        'europapress_parser.EuropaPressParser', datetime.utcnow()))
            self.feed_service.save(Feed('europa_press_nacional', 'http://www.europapress.es/rss/rss.aspx?ch=66',
                                        'europapress_parser.EuropaPressParser', datetime.utcnow()))
            self.feed_service.save(Feed('europa_press_economia', 'http://www.europapress.es/rss/rss.aspx?ch=136',
                                        'europapress_parser.EuropaPressParser', datetime.utcnow()))
            self.feed_service.save(Feed('europa_press_deporte', 'http://www.europapress.es/rss/rss.aspx?ch=67',
                                        'europapress_parser.EuropaPressParser', datetime.utcnow()))
            self.feed_service.save(Feed('clarin_extrashow', 'http://www.clarin.com/rss/extrashow/',
                                        'clarin_extrashow_parser.ClarinExtrashowParser', datetime.utcnow()))
            self.feed_service.save(Feed('telam_espectaculos', 'http://www.telam.com.ar/rss2/espectaculos.xml',
                                        'telam_espectaculos_parser.TelamEspectaculosParser', datetime.utcnow()))
            self.feed_service.save(Feed('lanacion_espectaculos',
                                        'http://servicios.lanacion.com.ar/herramientas/rss/categoria_id=120',
                                        'lanacion_espectaculos_parser.LaNacionEspectaculosParser', datetime.utcnow()))
            self.feed_service.save(Feed('cnet_esp', 'http://www.cnet.com/es/rss/',
                                        'cnet_esp_parser.CNetEspParser', datetime.utcnow()))
            self.feed_service.save(Feed('diario_america', 'http://www.diariolasamericas.com/rss/1_portada/index.rss',
                                        'diario_americas_parser.DiarioAmericasParser', datetime.utcnow()))
            self.feed_service.save(Feed('forbes_mexico', 'http://feeds.feedburner.com/ForbesMexico',
                                        'forbes_mexico_parser.ForbesMexicoParser', datetime.utcnow()))
            self.feed_service.save(Feed('informador_mexico', 'http://feeds.informador.com.mx/359/estados-unidos.rss',
                                        'informador_parser.InformadorParser', datetime.utcnow()))
            self.feed_service.save(Feed('miami_diario', 'http://www.miamidiario.com/rss/',
                                        'miamidiario_parser.MiamiDiarioParser', datetime.utcnow()))

    def crawl_all(self):
        crawler_logger.info("START crawl_all")
        entries = []
        crawler = Crawler()
        feeds_to_process = self.feed_service.get_feeds_to_process(self.feeds_to_process)

        for feed in feeds_to_process:
            news_entries = crawler.crawl(feed.parser, feed.url[0][0], feed.default_tags)
            entries.extend(news_entries)

        entries = self.discard_already_processed(entries)
        crawler_logger.info("END crawl_all")
        return self.__clean_duplicated(entries)

    def discard_already_processed(self, entries):
        crawler_logger.info("START Discarding already_processed urls")
        ns = NewsEntriesService()
        new_entries = []

        for entry in entries:
            if not ns.already_in_db(entry.url):
                new_entries.append(entry)

        crawler_logger.info("END Discarding already_processed urls")
        return new_entries

    def __clean_duplicated(self, entries):
        crawler_logger.info("START Discarding duplicated urls urls")
        cleaned_entries = []
        cleaned_entries_urls = []

        for entry in entries:
            if entry.url not in cleaned_entries_urls:
                cleaned_entries.append(entry)
                cleaned_entries_urls.append(entry.url)
        crawler_logger.info("END Discarding duplicated urls urls")
        return cleaned_entries
