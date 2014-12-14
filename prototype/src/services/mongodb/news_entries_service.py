from connector import MongoConnector
from src.sentinews.news_entry import NewsEntry

class NewsEntriesService(object):

	COLLECTION = 'news_entries'

	def __init__(self):
		self.db = MongoConnector.get_instance()
		self.news_entries = self.db[NewsEntriesService.COLLECTION]

	def save(self,news_entry):
		""" this method returns the objectId assigned"""

		return self.news_entries.insert(news_entry.to_dict())


	def delete(self,id):
		pass


	def get_list(self,criteria):
		""" Retrieve a list of new entries 
		Parameters
		----------
		criteria: dict 
			this is the object to use on mongodb find statement
		"""
		return [ NewsEntry(title=entry['title'], content=entry['content'],
			tags=entry['tags'], source=entry['source'], categories=entry['categories'],
			title_lematized=entry['title_lematized'], content_lematized=entry['content_lematized'],
			rewrite_content=entry['rewrite_content'])
		for entry in self.news_entries.find(criteria)]