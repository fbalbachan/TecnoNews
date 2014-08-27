# -*- coding: utf-8 -*-
import unittest
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.blog_publisher import Entry

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
        BlogPublisher.HOST = ''
        BlogPublisher.USER = ''
        BlogPublisher.PASS = ''

        content = 'Hola. <a href=http://www.google.com>Link de prueba</a>.'
        entry = Entry('Hola',content,['test', 'sentinews'], 'fuente_de_prueba')
        self.blog_publisher._publish_entry(entry)

if __name__ == '__main__':
    unittest.main()
