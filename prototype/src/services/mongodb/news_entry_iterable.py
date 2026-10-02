# -*- coding: utf-8 -*-
from src.sentinews.news_entry import NewsEntry

class NewsEntryIterable(object):

    def __init__(self, mongo_cursor=None):
        self.cursor = mongo_cursor

    def __next__(self):
        ret_entry = None

        try:
            entry = next(self.cursor)
            ret_entry = NewsEntry(
                              title=entry['title'] if 'title' in entry else None,
                              content=entry['content'] if 'content' in entry else None,
                              tags=entry['tags'] if 'tags' in entry else None,
                              source=entry['source'] if 'source' in entry else None,
                              url=entry['url'] if 'url' in entry else None,
                              categories=entry['categories'] if 'categories' in entry else ["None"],
                              published_date=entry['published_date'] if 'published_date' in entry else None,
                              entities=entry['entities'] if 'entities' in entry else None,
                              wp_id=entry['wp_id'] if 'wp_id' in entry else None,
                              wp_url=entry['wp_url'] if 'wp_url' in entry else None,
                              related=entry['related'] if 'related' in entry else None,
                              object_id=entry['_id'] if '_id' in entry else None,
                              versions=entry['versions'] if 'versions' in entry else None,
                              universe_versions=entry['universe_versions'] if 'universe_versions' in entry else None,
                              summary=entry['summary'] if 'summary' in entry else None,
                              extended_summary=entry['extended_summary'] if 'extended_summary' in entry else None)
        except StopIteration:
            ret_entry = None

        return ret_entry
