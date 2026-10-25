# -*- coding: utf-8 -*-
from collections import deque


class ParagraphEntityTagger:
    def tag_with_main_entities(self, text, entities, tag_name, attrib_by_entity=None):
        '''This doesn't look at the entities children.'''

        if attrib_by_entity is None:
            attrib_by_entity = {}

        entities = [entity for entity in set(entities) if not entity.is_tacit()]
        entities = [p_entity for p_entity in entities if p_entity.is_maximal_regarding(entities)]
        entities.sort(key=lambda p_entity: p_entity.token.start())

        tag_mapping = {}
        tagged_text = ""
        entity_id = 0
        index = 0

        for entity in entities:
            start = entity.token.start()
            end = entity.token.end()
            entity_text = text[start:end]
            tagged_text += text[index:start]
            tagged_text += "<%s id='e_%s'" % (tag_name, str(entity_id))
            if entity in attrib_by_entity:
                for attrib in attrib_by_entity[entity]:
                    tagged_text += " %s=%s" % (attrib, attrib_by_entity[entity][attrib])
            tagged_text += ">%s</%s>" % (entity_text, tag_name)
            tag_mapping[entity] = "e_%s" % (str(entity_id))
            index = end
            entity_id += 1
        tagged_text += text[index:]

        return tagged_text, tag_mapping

    def tag_with_entities(self, text, entities, tag_name, attrib_by_entity=None):

        if attrib_by_entity is None:
            attrib_by_entity = {}

        entities = [entity for entity in set(entities) if not entity.is_tacit()]
        entities = [p_entity for p_entity in entities if p_entity.is_maximal_regarding(entities)]
        entities.sort(key=lambda p_entity: p_entity.token.start())

        tag_mapping = {}
        entities = deque(entities)
        close_tag_deque = deque()
        tagged_text = ""
        entity_id = 0
        index = 0
        while entities:
            entity = entities.popleft()

            start = entity.token.start()
            end = entity.token.end()

            if entity.children:
                reversed_children = entity.children[::-1]
                close_tag_deque.appendleft((reversed_children[0], end))
                entities.extendleft(reversed_children)
                end = entities[0].token.start()

            entity_text = text[start:end]

            tagged_text += text[index:start]
            tagged_text += "<%s id='e_%s'" % (tag_name, str(entity_id))
            if entity in attrib_by_entity:
                for attrib in attrib_by_entity[entity]:
                    tagged_text += " %s=%s" % (attrib, attrib_by_entity[entity][attrib])
            tagged_text += ">%s" % entity_text
            if not entity.children:
                tagged_text += "</%s>" % (tag_name)

            tag_mapping[entity] = "e_%s" % (str(entity_id))

            index = end
            entity_id += 1

            if close_tag_deque and close_tag_deque[0][0] == entity:
                pending_end = close_tag_deque.popleft()[1]
                tagged_text += text[index:pending_end] + "</%s>" % (tag_name)
                index = pending_end

        tagged_text += text[index:]

        tagged_text = tagged_text.replace("\n", "<br>")
        return tagged_text, tag_mapping

    def tag_all(self, paragraph, tag_name):
        return self.tag_with_entities(paragraph.text, paragraph.entities(), tag_name)
