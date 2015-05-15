# -*- coding: utf-8 -*-
import wikipedia as wk
import urllib
import json
import urllib
from collections import defaultdict
from src.model.output.paragraphEntityTagger import ParagraphEntityTagger
from src.utils.logger_utils import *
import traceback
import datetime


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

        # This has the form: {entity : {link_type: link}}
        # where link_type = 'google', 'wiki', 'linkedin', 'maps', 'lucky'
        self.links_by_entity = defaultdict(dict)
        wk.set_lang('es')

    def get_text_with_hyperlinks(self):
        ''' Get all hyperlinks, format to html and add to text. 

            Returns: a String with the text.'''
        self._fetch_all_links()
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
        self._get_linkedIn_links()
        self._get_gMaps_links()
        self._get_web_page_links()
        #self._get_other_links()
        self._get_wikipedia_links()

    def _get_linkedIn_links(self):
        for entity in self.entities:
            if entity.classification() == 'person':
                if 'names' in entity.attributes and 'surnames' in entity.attributes:
                    person = " ".join(entity.attributes['names']) + " " + " ".join(entity.attributes['surnames'])
                    link = self._get_first_gresult(LINKEDIN_GQUERY + person)
                    if link != '':
                        self.links_by_entity[entity]['linkedin'] = link
                else:
                    if 'names' in entity.attributes:  # not 'surnames' in entity.attributes is implied
                        person = entity.attributes['names']
                    elif 'surnames' in entity.attributes:
                        person = entity.attributes['surnames']
                    else:
                        # If doesn't have name or surname continue with the next case
                        continue

                    person = " ".join(person)
                    self.links_by_entity[entity]['google'] = (GSEARCH_BASE_URL + urllib.quote_plus(person))


    def _get_gMaps_links(self):
        for entity in self.entities:
            if entity.classification() == 'place':
                search_string = ''
                if 'class' in entity.attributes:
                    search_string += " ".join(entity.attributes['class']) + " "
                search_string +=  str(entity.kernel)
                self.links_by_entity[entity]['maps'] = (GMAPS_BASE_URL + urllib.quote(search_string))
    
    def _get_web_page_links(self):
        for entity in self.entities:
            if entity.classification() == 'organization':
                search_string = str(entity.kernel)
                if 'names' in entity.attributes:
                    search_string = " ".join(entity.attributes['names'])
                self.links_by_entity[entity]['lucky'] = self._get_first_gresult(search_string)

    def _get_other_links(self):
        for entity in self.entities:
            if entity.classification() == 'other':
                search_string = str(entity.kernel).replace('_', ' ')
                self.links_by_entity[entity]['google'] = (GSEARCH_BASE_URL + urllib.quote_plus(search_string))

    def _get_wikipedia_links(self):
        ''' Searches Wikipedia for each Entity, uses first result to form URL. '''
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
                self.links_by_entity[entity]['wiki'] = (WIKI_BASE_URL + encoded_result)
            else:
                self.links_by_entity[entity]['google'] = (GSEARCH_BASE_URL + urllib.quote_plus(search_string))

    def _add_links_to_text(self):
        attrib_by_entity = {}
        for entity in self.links_by_entity:
            link = self._choose_link(entity)
            attrib_by_entity[entity] = {'href': link,
                                        'target':'_blank'}
        keys = attrib_by_entity.keys()
        for entity in self.paragraph.entities():
            for main_entity in keys:
                if entity != main_entity and entity.referent == main_entity.referent:
                    attrib_by_entity[entity] = attrib_by_entity[main_entity]

        tagger = ParagraphEntityTagger()
        entities = [entity for  entity in self.paragraph.entities() if entity in attrib_by_entity]
        (tagged_text, tag_mapping) = tagger.tag_with_main_entities(self.paragraph.text, 
                                                                   entities, 
                                                                   'a',
                                                                   attrib_by_entity)

        return tagged_text
    
    def _choose_link(self, entity):
        if entity.classification() == 'person':
            for link_type in ['linkedin', 'wiki']:
                if link_type in self.links_by_entity[entity]:
                    return self.links_by_entity[entity][link_type]
        elif entity.classification() == 'place':
            for link_type in ['maps', 'wiki']:
                if link_type in self.links_by_entity[entity]:
                    return self.links_by_entity[entity][link_type]
        elif entity.classification() == 'organization':
            for link_type in ['wiki','linkedin']:
                if link_type in self.links_by_entity[entity]:
                    return self.links_by_entity[entity][link_type]
        return ''
        
    def _google_search(self, searchfor):
        query = urllib.urlencode({'q': searchfor})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
        search_results = urllib.urlopen(url).read()
        return json.loads(search_results)

    def _get_first_gresult(self, searchfor):
        data = self._google_search(searchfor)
        first_result = None

        try:
            if data:
                results = data.get('responseData', {}).get('results')
                if len(results) > 0:
                    first_result = results[0].get('url', {})

        except Exception as e:
            logger = get_logger('tecnonews')
            logger.info("HyperlinkProcessor:")
            logger.info("Searchfor: %s", searchfor)
            logger.info("JSON %s" % data)
            logger.info(traceback.format_exc())
            logger.info("%s" % e.message)

        if not first_result:
            first_result = ''

        return first_result
