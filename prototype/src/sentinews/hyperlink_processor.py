# -*- coding: utf-8 -*-
import wikipedia as wk
import urllib

WIKI_BASE_URL = 'http://es.wikipedia.org/wiki/'

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
        wk.set_lang('es')

    def get_text_with_hyperlinks(self):
        ''' Get all hyperlinks, format to html and add to text. 

            Returns: a String with the text.'''
        links = self._get_all_links()
        return self._add_links_to_text(links)

    def _get_entities_from(self, paragraph):
        ''' Filter entities, keeping only the ones that have "classification" '''
        return [entity for entity in paragraph.entities() if entity.classification()]

    def _get_all_links(self):
        ''' Search links in: LinkedIn, GMaps, Wikipedia and organization webpage.
            Returns: a list with all the hyperlinks. '''
        links = []

        links += self._get_linkedIn_links()
        links += self._get_gMaps_links()
        links += self._get_web_page_links()
        links += self._get_wikipedia_links()

        return links

    def _get_linkedIn_links(self):
        return []

    def _get_gMaps_links(self):
        return []    

    def _get_web_page_links(self):
        return []    

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
                    search_string += " ".join(entity.attributes['class'])
                search_string += str(entity.kernel)

            search_result = wk.search(search_string)
            if search_result:
                encoded_result = urllib.quote(search_result[0].encode('utf-8')) 
                links.append(WIKI_BASE_URL + encoded_result)
        return links

    def _add_links_to_text(self, links):
        return ""