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

        self.blog_publisher = BlogPublisher()

    
    def test_publish(self):
        # Completar con datos de testing
        #Must have .../xmlrpc.php
        import src.sentinews.blog_publisher
        src.sentinews.blog_publisher.HOST = 'http://tecnonews.comule.com/xmlrpc.php'
        src.sentinews.blog_publisher.USER = 'tecnonews'
        src.sentinews.blog_publisher.PASS = 'tecnonews1'

        content = 'Hola. <a href=http://www.google.com>Link de prueba</a>. y mas texto no analizado'
        entry = NewsEntry('Hola, a diego le gusta hacer pruebas',content,['salud', 'droga'], 'fuente_de_prueba')
        print entry.destination
        self.blog_publisher.publish(entry)
        print entry.wp_id


    def test_publish_tecnologia(self):
        # Completar con datos de testing
        #Must have .../xmlrpc.php
        import src.sentinews.blog_publisher
        src.sentinews.blog_publisher.HOST = 'http://tecnonews.comule.com/xmlrpc.php'
        src.sentinews.blog_publisher.USER = 'tecnonews'
        src.sentinews.blog_publisher.PASS = 'tecnonews1'

        content = 'Hola. <a href=http://www.google.com>Link de prueba</a>. en la seccion de autos publicado una sola vez'
        entry = NewsEntry('Hola, a diego le gusta hacer pruebas',content,['automovilismo', 'aplicación', 'festival'], 'fuente_de_prueba')
        self.blog_publisher.publish(entry)

if __name__ == '__main__':
    unittest.main()
