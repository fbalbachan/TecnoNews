# -*- coding: utf-8 -*-
import unittest
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry

class TestBlogPublisher(unittest.TestCase):

    def setUp(self):
        links = ['http://es.wikipedia.org/wiki/Telef%C3%B3nica', 
                 'http://es.wikipedia.org/wiki/Calle%20Florida', 
                 'http://es.wikipedia.org/wiki/Thomas%20P.%20Griesa', 
                 ]

        self.blog_publisher = BlogPublisher("", links)
    

    def test__format_html_links(self):
        html_links = self.blog_publisher._format_html_links()
        self.assertIn('<a href=http://es.wikipedia.org/wiki/Telef%C3%B3nica>http://es.wikipedia.org/wiki/Telef%C3%B3nica</a>', html_links)

    
    def test_publish(self):
        # Completar con datos de testing
        #Must have .../xmlrpc.php
        import src.sentinews.blog_publisher
        src.sentinews.blog_publisher.HOST = 'http://tecnonews.comule.com/xmlrpc.php'
        src.sentinews.blog_publisher.USER = 'tecnonews'
        src.sentinews.blog_publisher.PASS = 'tecnonews1'

        content = 'Hola. <a href=http://www.google.com>Link de prueba</a>.'
        entry = NewsEntry('Hola',content,['test', 'sentinews'], 'fuente_de_prueba')
        self.blog_publisher._publish_entry(entry)

if __name__ == '__main__':
    unittest.main()
