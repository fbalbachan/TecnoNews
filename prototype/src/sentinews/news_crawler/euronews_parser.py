from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *


class EuroNewsParser(object):
    base_path = 'http://es.euronews.com'
    source = u'EuroNews'

    def parse(self, url, limit=1):
        soup = BeautifulSoup(urlopen(url).read())
        articles = soup.find(
            'ul', {'id': 'bulletin-list'}).find_all('li', limit=limit)

        new_entries = []
        for article in articles:
            title = title = article.find(
                'span', {'class': 'bulletin-title'}).text[12:]
            content, tags = self.___extract_content(article)
            new_entries.append(NewsEntry(title, content, tags, self.source))

        return new_entries


    def ___extract_content(self, article):
        article_url = article.find('a', {'class': 'read-more-button'})['href']
        soup = BeautifulSoup(urlopen(self.base_path + article_url).read())

        content_paragraphs_list = [paragraph.text for paragraph in soup.find('div', {'id': 'articleTranscript'}).find_all('p')]
                
        content_str = ['<p>' + text + '</p>' for text in content_paragraphs_list]
        li_tags = soup.find('ul', {'class': 'kwl'}).find_all('li')
        tags = [tag.find('a').text for tag in li_tags]
        return " ".join(content_str), tags
