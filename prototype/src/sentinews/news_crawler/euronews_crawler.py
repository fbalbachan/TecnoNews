from crawler import Crawler
from euronews_parser import EuroNewsParser


class EuroNewsCrawler(Crawler):


	boletin_url = 'http://es.euronews.com/noticias/boletin/' 
	

	def crawl(self):
        peuro = EuroNewsParser()
        raw_entries = peuro.parse(self.boletin_url, 3)
        filtered_entries = self._filter_entries(entries)
        for entry in filtered_entries:
            news_entry = parser.parse(entry["link"])
            news_entries.append(news_entry)
        return self._filter_by_tag(news_entries)
