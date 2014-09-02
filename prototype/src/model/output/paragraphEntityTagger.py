# -*- coding: utf-8 -*-
from collections import deque

from src.model.entity.entity import Entity


class ParagraphEntityTagger:
    def tag(self, text, paragraph):
        text = text.decode("utf-8")

        tag_mapping = {}
        entities = [ entity for entity in set(paragraph.entities()) if not entity.is_tacit() ]
        entities = Entity.only_maximal(entities)
        entities.sort(key = lambda entity: entity.token.start())

        entities = deque(entities)
        close_tag_deque = deque()

        #for entity in entities:
        #    print entity, entity.token, entity.proper_node.leaves()

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
            tagged_text += "<span id='e_" + str(entity_id) + "'>" + entity_text
            if not entity.children: tagged_text += "</span>"

            tag_mapping[entity] = "e_" + str(entity_id)

            index = end
            entity_id += 1

            if close_tag_deque and close_tag_deque[0][0] == entity:
                pending_end = close_tag_deque.popleft()[1]
                tagged_text += text[index:pending_end] + "</span>"
                index = pending_end

        tagged_text += text[index:]

        print tagged_text
        return (tagged_text, tag_mapping)
