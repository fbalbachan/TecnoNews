#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import itertools
from conf import *
from estructura import *
from palabra import *
from oracion import *
from texto import *
from est import *
from sentiment import *
from utils.tokenize import sentence_delimiters

logger    = logging.getLogger('sentitext')
handler   = logging.FileHandler('logs/sentitext.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

def resolver_subordinante(clause, sentence_containing_this_clause):
    subordinante = clause.subordinante
    logger.info("(%d %s %s %s) buscando antecedente..." % (subordinante.position, subordinante.form, subordinante.genero, subordinante.numero))

    palabra_previa_al_subordinante = filter(lambda w: w.position == subordinante.position - 1, sentence_containing_this_clause.all.words)[0]
    logger.info("palabra_previa_al_subordinante %s" % palabra_previa_al_subordinante)
    if palabra_previa_al_subordinante.form in preposiciones_para_subordinada_oblicua:
        es_oblicua = True
    else:
        es_oblicua = False
    logger.info("es oblicua: " + str(es_oblicua))

    verbo_subordinada = clause.verbs[0].words[0]
    info_verbo = verbo_subordinada.tag[-3:]
    persona_verbo_subordinada, numero_verbo_subordinada, extra_verbo_subordinada = info_verbo[0], info_verbo[1], info_verbo[2]
    logger.info("verbo_subordinada: %s %s %s %s" % (verbo_subordinada, persona_verbo_subordinada, numero_verbo_subordinada, extra_verbo_subordinada))
    
    if not(es_oblicua):
        if subordinante.form.lower() == 'que':
            for previous_clause in reversed(sentence_containing_this_clause.clauses[:clause.nivel]):
                candidatos = previous_clause.entidades_sujeto + previous_clause.entidades_no_sujeto
                logger.info("candidatos no oblicua que: %s" % candidatos)
                if candidatos:
                    antes = filter(lambda x: x.words[0].position < clause.words[0].position, candidatos)
                    logger.info("antes: %s" % antes)
                    if antes:
                        candidato_proximo_al_que = list(reversed(sorted(antes, key=lambda clause: clause.words[0].position)))[0]
                        logger.info("candidato no oblicua que proximo al que: %s" % candidato_proximo_al_que)
                        logger.info("match (que)! %s <- %s" % (subordinante.form, candidato_proximo_al_que))
                        clause.sujeto = candidato_proximo_al_que
                        break
        else:
            for previous_clause in reversed(sentence_containing_this_clause.clauses[:clause.nivel]):
                candidatos = previous_clause.entidades_sujeto + previous_clause.entidades_no_sujeto
                logger.info("candidatos no oblicua no que: %s" % candidatos)
                for candidato in candidatos:
                    if subordinante.numero == candidato.numero and subordinante.genero == candidato.genero:
                        logger.info("match (!= que)! %s <- %s" % (subordinante.form, candidato))
                        clause.sujeto = candidato
                        break
    else:
        if subordinante.form.lower() == 'que':
            for previous_clause in reversed(sentence_containing_this_clause.clauses[:clause.nivel]):
                candidatos = previous_clause.entidades_sujeto + previous_clause.entidades_no_sujeto
                logger.info("candidatos oblicua que: %s" % candidatos)
                if candidatos:
                    candidatos = filter(lambda x: x.nucleo()[2] == verbo_subordinada.numero, candidatos)
                    antes = filter(lambda x: x.words[0].position < clause.words[0].position, candidatos)
                    if antes:
                        candidato_proximo_al_que = list(reversed(sorted(antes, key=lambda clause: clause.words[0].position)))[0]
                        logger.info("match (que)! %s <- %s" % (subordinante.form, candidato_proximo_al_que))
                        label_candidato, genero_candidato, numero_candidato = candidato_proximo_al_que.nucleo()
                        logger.info("numero candidato: ", numero_candidato)
                        # if numero_candidato == numero_verbo_subordinada:
                        clause.sujeto = candidato_proximo_al_que
                        break
                        
        else:
            for previous_clause in reversed(sentence_containing_this_clause.clauses[:clause.nivel]):
                candidatos = previous_clause.entidades_sujeto + previous_clause.entidades_no_sujeto
                logger.info("candidatos oblicua no que: %s" % candidatos)
                for candidato in candidatos:
                    if subordinante.numero == candidato.numero and subordinante.genero == candidato.genero:
                        logger.info("match (!= que)! %s <- %s" % (subordinante.form, candidato))
                        clause.sujeto = candidato
                        break

    return clause
    
def extract_entities(input_text):
    entities = []

    text = Texto(); # logger.info('-'*80); logger.info('nuevo texto\n'+' '*80)
    # input_sentences = [s.strip() for s in filter(lambda x: not(x.startswith('#')), input_text)]
    input_sentences = [s.strip() for s in re.split(sentence_delimiters, input_text, re.U)]
    input_sentences = filter(lambda s: s != u'' and s != None, input_sentences)
    for i, input_sentence in enumerate(input_sentences): logger.info("input sentence: %d) '%s'" % (i, input_sentence))
    sentences = filter(lambda s: s.valid, [Oracion(input_sentence) for input_sentence in input_sentences])

    for sentence_id, sentence in enumerate(sentences):
        sentence.id = sentence_id
        # logger.info('.'*80); logger.info("sentence: %d) '%s'" % (sentence.id, sentence.input_text))

        for i, clause in enumerate(sentence.clauses):
            # logger.info("cláusula: '%s' principal: %s" % (clause, clause.principal and 'sí' or 'no'))
                        
            go = clause.contenidas_en(global_operator_words)
            if go:
                clause.contiene_global_operator = True
                clause.svo.global_operator = GlobalOperator(filter(lambda (a,b,c): a == go[0], global_operators)[0])
                # logger.info("global operator %s" % clause.svo.global_operator)

            if clause.is_whole_sentence:
                clause.svo.asignar_sentimiento()
                # logger.info("clause.svo: %s" % clause.svo)
                continue

            clause.hallar_entidades()

            clause.hallar_subordinante()
            if clause.subordinante: clause = resolver_subordinante(clause, sentence)

            clause.hallar_sujeto()
            clause.hallar_SVO()
            if clause.svo:
                # si hay sujeto pronominal forma tercera, buscarlo más abajo:
                if len(clause.svo.subject.words) == 1 and clause.svo.subject.words[0].form.lower() in formas_terceras:
                    clause.sujeto_es_pronominal = True
                    # logger.info("clause.svo.subject es pronominal: %s" % clause.svo.subject.words[0])
                # si hay objeto forma tercera, resolverlo:
                if len(clause.svo.object.words) == 1 and clause.svo.object.words[0].lemma in formas_terceras:
                    clause.objeto_es_pronominal = True
                    # logger.info("clause.svo.object es pronominal: %s" % clause.svo.object.words[0])
                
                clause.svo.asignar_sentimiento()
                # logger.info("clause.svo %s" % clause.svo.__str__())
            
            clause_entities = []
            clause_entities.append(clause.svo.subject)
            clause_entities.append(clause.svo.object)
            clause_entities.extend(clause.svo.others)

            for entity in filter(lambda e: e.__str__() != 'x', clause_entities):
                entity.sentence_id = sentence_id
                entities.append(entity)

        text.add(sentence)

    # logger.info('.'*80); logger.info("text: %s" % text)

    # resolver antecedentes inter-oración:
    for sentence in text.sentences:
        main_clauses = filter(lambda c: c.principal, sentence.clauses)
        for main_clause in main_clauses:

            # encontrar antecedente sujeto tácito / pronominal
            if (main_clause.sujeto_es_tacito and len(main_clause.sujeto.words) == 1 and main_clause.sujeto.words[0].form.lower() in formas_terceras) or main_clause.sujeto_es_pronominal:
                # logger.info("buscando antecedente sujeto tácito / pronominal: %s" % main_clause.sujeto)
                found_antecedente = False
                
                # 1) por paralelismo sintáctico (buscar sujeto de la oración anterior) 
                for previous_sentence in reversed(text.sentences[:sentence.id]):
                    # logger.info("previous sentence: %s" % previous_sentence)
                    main_previous_clause = filter(lambda c: c.principal, previous_sentence.clauses)[0]
                    # logger.info("checking (paralelismo sintáctico) %s" % main_previous_clause.sujeto)
                    if main_previous_clause.sujeto.numero == main_clause.sujeto.numero and main_previous_clause.sujeto.genero == main_clause.sujeto.genero:
                        # logger.info("match antecedente sujeto: %s <- %s" % (main_previous_clause.sujeto, main_clause.sujeto))
                        sentimiento_actual = main_previous_clause.svo.subject.get_sentiment()
                        main_clause.svo.subject = copy.deepcopy(main_previous_clause.svo.subject)
                        main_clause.svo.subject.sentiment = sentimiento_actual
                        # logger.info(main_clause.svo)
                        found_antecedente = True
                        break
                    else:
                        # 2) por recencia (buscar sujeto en todas las entidades de cláusulas de la oración anterior):
                        non_main_previous_clauses = filter(lambda c: not(c.principal), previous_sentence.clauses)
                        for previous_clause in sorted(previous_sentence.clauses, key=lambda c: c.all.start, reverse=True):
                            candidatos = sorted([previous_clause.svo.subject, previous_clause.svo.object], key=lambda x: x.words[0].position, reverse=True)
                            # separar esto, para no pisar
                            for candidato in candidatos:
                                nucleo_candidato, (candidato_label, candidato_genero, candidato_numero) = candidato.estructura.nucleo()
                                # logger.info("checking (recencia): %s" % candidato)
                                if candidato_numero == main_clause.sujeto.numero and candidato_genero == main_clause.sujeto.genero:
                                    # logger.info("match antecedente sujeto: %s <- %s" % (main_clause.sujeto, candidato))
                                    sentimiento_actual = candidato.get_sentiment()
                                    main_clause.svo.subject = copy.deepcopy(candidato)
                                    main_clause.svo.subject.sentiment = sentimiento_actual
                                    # logger.info(main_clause.svo)
                                    found_antecedente = True
                                    break

                if not(found_antecedente):
                    logger.info("no match antecedente sujeto")

    svos = filter(lambda x: x != SVO(), [clause.svo for sentence in text.sentences for clause in sentence.clauses])

    # logger.info('.'*80); logger.info("extraer_entidades - entidades: %s" % ' - '.join([e.__str__() for e in entities]))
    # logger.info('.'*80); logger.info("extraer_entidades - svos: %s" % ' - '.join([svo.__str__() for svo in svos]))
    return svos, entities

def format_entities(entities):
    entidades_ordenadas = sorted(entities, key=lambda e: e.estructura.__str__())
    # logger.info('.'*80); logger.info("entidades (candidatos): %s" % ' - '.join([e.__str__() for e in entidades_ordenadas]))

    entities_final = []
    groups = itertools.groupby(entidades_ordenadas, lambda e: e.estructura.sin_determinantes().__str__())
    for (representacion, lista_de_entidades) in groups:
        others = list(lista_de_entidades)
        if len(others) > 1:
            original = others[0]
            entities_final.append(original)
            for other_entity in others[1:]:
                if other_entity.sentence_id - original.sentence_id <= 3:
                    original.add_sentiment(other_entity.get_sentiment())
                else:
                    entities_final.append(other_entity)
        else:
            entities_final.append(others[0])
        
    return entities_final


if __name__ == '__main__':
    input_text = codecs.open('input.txt', 'r', 'utf-8').readlines()

    svos, entities = extract_entities(input_text)
    entities_with_sentiment = format_entities(entities)

    # logger.info('.'*80)
    for e in entities_with_sentiment:
        # logger.info("%s (sentence id: %d) -> %s" % (e, e.sentence_id, e.get_sentiment()))
        print "%s (sentence id: %d) -> %s" % (e, e.sentence_id, e.get_sentiment())

    for svo in svos: print "%s" % svo
