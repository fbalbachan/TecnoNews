from crawler import Crawler
from euronews_parser import EuroNewsParser


class EuroNewsCrawler(Crawler):
	
    boletin_url = 'http://es.euronews.com/noticias/boletin/'
   
    def crawl(self):
        peuro = EuroNewsParser()
        raw_entries = peuro.parse(self.boletin_url, 5)
        filtered_entries = self._filter_entries(raw_entries)
        return self._filter_by_tag(filtered_entries)
