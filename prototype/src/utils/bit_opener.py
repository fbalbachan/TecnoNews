from urllib import FancyURLopener
from random import choice


class BitOpener(FancyURLopener, object):

    def __init__(self):
        user_agents = [
            'Mozilla/5.0 (X11; Linux i586; rv:31.0; es-ES) Gecko/20100101 Firefox/31.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; es-ES: rv:33.0) Gecko/20100101 Firefox/33.0',
            'Mozilla/5.0 (X11; Linux 3.5.4-1-ARCH i686; es-ES) KHTML/4.9.1 (like Gecko) Konqueror/4.9',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1; es-ES) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; es-ES) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        ]

        super(BitOpener, self).__init__()
        self.version = choice(user_agents)