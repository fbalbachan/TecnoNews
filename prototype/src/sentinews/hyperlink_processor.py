# -*- coding: utf-8 -*-
import wikipedia as wk
import urllib
import json
import urllib


WIKI_BASE_URL = 'http://es.wikipedia.org/wiki/'
LINKEDIN_GQUERY = 'site:linkedin.com '
GMAPS_BASE_URL = 'https://maps.google.com/maps?q='
GSEARCH_BASE_URL = 'https://www.google.com.ar/search?q='

class HyperlinkProcessor(object):
    """Given a Sentilecto analysis with Entities, adds hyperlinks.
       
       These hyperlinks can be of different types: 
       * LinkedIn profile for a given person.
       * Google Maps location for a given place.
       * Webpage for an organization.
       * Wikipedia or Google results for other entities.
    """
    
    def __init__(self, analysis):
        self.paragraph = analysis['paragraph']
        self.entities = self._get_entities_from(analysis['paragraph'])
        self.links = []
        wk.set_lang('es')

    def get_text_with_hyperlinks(self):
        ''' Get all hyperlinks, format to html and add to text. 

            Returns: a String with the text.'''
        self._fetch_all_links()
        print self.links
        return self._add_links_to_text()

    def _get_entities_from(self, paragraph):
        ''' Filter entities, keeping only the ones that have "classification" '''
        entities =  [entity for entity in paragraph.entities() if entity.classification()]
        references = []
        added_references = []
        for x in entities:
            if x.referent.name() not in added_references:
                references.append(x)
                added_references.append(x.referent.name())
        return references

    def _fetch_all_links(self):
        ''' Search links in: LinkedIn, GMaps, Wikipedia and organization webpage.
            Returns: a list with all the hyperlinks. '''
        self.links += self._get_linkedIn_links()
        self.links += self._get_gMaps_links()
        self.links += self._get_web_page_links()
        self.links += self._get_other_links()
        self.links += self._get_wikipedia_links()

    def _get_linkedIn_links(self):
        links = []
        for entity in self.entities:
            if entity.classification() == 'person':
                if 'names' in entity.attributes and 'surnames' in entity.attributes:
                    person = " ".join(entity.attributes['names']) + " " + " ".join(entity.attributes['surnames'])
                    links.append(self._google_search(LINKEDIN_GQUERY + person)) 
        return links

    def _get_gMaps_links(self):
        links = []
        for entity in self.entities:
            if entity.classification() == 'place':
                search_string = ''
                if 'class' in entity.attributes:
                    search_string += " ".join(entity.attributes['class']) + " "
                search_string +=  str(entity.kernel)
                links.append(GMAPS_BASE_URL + urllib.quote(search_string))
        return links
    
    def _get_web_page_links(self):
        return []

    def _get_other_links(self):
        links = []
        for entity in self.entities:
            if entity.classification() == 'other':
                search_string = str(entity.kernel).replace('_', ' ')
                links.append(GSEARCH_BASE_URL + urllib.quote_plus(search_string))
        return links   

    def _get_wikipedia_links(self):
        ''' Searches Wikipedia for each Entity, uses first result to form URL. '''
        links = []
        for entity in self.entities:
            search_string = ''
            if entity.classification() == 'person':
                for attribute in ['names', 'surnames']:
                    if attribute in entity.attributes:
                        search_string += " ".join(entity.attributes[attribute])
            elif entity.classification() == 'organization':
                if 'names' in entity.attributes:
                    search_string += " ".join(entity.attributes['names'])
            elif entity.classification() == 'place':
                if 'class' in entity.attributes:
                    search_string += " ".join(entity.attributes['class']) + " "
                search_string += str(entity.kernel)

            if search_string == '': continue
            search_result = wk.search(search_string)
            if search_result:
                encoded_result = urllib.quote(search_result[0].encode('utf-8')) 
                links.append(WIKI_BASE_URL + encoded_result)
        return links

    def _add_links_to_text(self):
        import pudb;pu.db
        return ""

    def _google_search(self, searchfor):
        query = urllib.urlencode({'q': searchfor})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
        search_results = urllib.urlopen(url).read()
        return json.loads(search_results)['responseData']['results'][0]['url']


