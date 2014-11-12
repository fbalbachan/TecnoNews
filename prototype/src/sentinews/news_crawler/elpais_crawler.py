from crawler import Crawler
from elpais_parser import ElPaisParser


class ElPaisCrawler(Crawler):
	
    boletin_url = 'http://elpais.com/tag/fecha/hoy'
   
    def crawl(self):
        peuro = ElPaisParser()
        raw_entries = peuro.parse(self.boletin_url, 4)
        filtered_entries = self._filter_entries(raw_entries)
        return self._filter_by_tag(filtered_entries)
