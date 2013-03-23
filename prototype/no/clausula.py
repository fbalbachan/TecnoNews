#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, logging
from est import *
from estructura import *
from utils.utils import *
from utils.tokenize import *
from utils.ling import *
from svo import *

logger    = logging.getLogger('clausula')
handler   = logging.FileHandler('logs/clausula.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def traverse(struct):
    for child in struct.children:
        yield child
        if child.children:
            traverse(child)

class Clausula(object):
    def __init__(self, estructura, hija_de_coord=False):
        # to be filled later
        self.entidades_sujeto = []
        self.entidades_no_sujeto = []
        self.entidades_privativa = []
        self.subordinante = None
        self.sujeto = None
        self.sujeto_es_pronominal = False
        self.objeto_es_pronominal = False
        self.sujeto_es_tacito = False
        self.pasiva = False
        self.modal = None
        self.contiene_global_operator = False
        self.contiene_local_shifter = False
        self.svo = SVO()
        # fill now
        self.hija_de_coord = hija_de_coord
        self.nivel = estructura.nivel
        self.principal = (self.nivel == 0 and True) or (self.nivel == 1 and hija_de_coord) or False
        self.is_whole_sentence = False
        self.all = estructura
        self.words = self.all.words
        # logger.info('.'*80); logger.info("words: %s" % ' '.join([w.__str__() for w in self.words]))
        self.lemmas = [w.lemma for w in self.words]
        self.flatstructs = list(traverse(self.all))
        self.verbs = self.by_label('verb') or []
        self.verbs.extend(self.by_label('parti-flex')) # participios, p.ej. 'comido'
        if self.by_label('parti-flex'): self.pasiva = True
        # if self.pasiva: logger.info("es pasiva: %s" % self.by_label('parti-flex')[0].words[0].form)
        if self.verbs:
            for v in self.verbs:
                if len(v.words) > 1:
                    if v.words[0].lemma in [u'poder', u'querer', u'soler', u'deber', u'estar', u'necesitar']:
                        self.modal = ModalVerb(v.words[0])
                        v.words[1].tag = v.words[0].tag
                        v.words = [v.words[-1:][0]]  # v.words[-1:][0] -> last v.words
                    elif v.words[0].lemma == 'haber':
                        v.words[1].tag = v.words[0].tag
                        v.words = [v.words[-1:][0]]

    def __repr__(self):
        return u'%s[%s]' % (self.all.label, self.all.forms())

    def __str__(self):
        return self.all.__str__()

    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)

    def contenidas_en(self, list_of_words):
        return list(set([w.lower() for w in self.all.forms()]).intersection(set(list_of_words)))

    def hallar_sujeto(self):
        if not self.verbs: return
        primer_verbo = sorted(self.verbs, key=lambda x: x.start)[0]
        if primer_verbo.label == 'verb':
            info_verbo = primer_verbo.words[0].tag[-3:]
        elif primer_verbo.label == 'parti-flex':
            posicion_participio = primer_verbo.words[0].position
            ser_conjugado = filter(lambda x: x.position == posicion_participio - 1, self.words)[0]
            info_verbo = ser_conjugado.tag[-3:]
        persona_verbo, nro_verbo, extra_verbo = info_verbo[0], info_verbo[1], info_verbo[2]

        entidades_a_izquierda = self.entidades_sujeto
        for entidad in entidades_a_izquierda:
            nucleo, (label, genero, numero) = entidad.nucleo()
            logger.info(u"entidad a izquierda: %s %s %s %s" % (nucleo, label, genero, numero))
            if nucleo:
                matching_word = nucleo.words[0]
                if (nro_verbo == numero) and persona_verbo == '3':
                    self.sujeto = entidad
                    break
                if (((persona_verbo == '2') and (nro_verbo == 'S') and
                     (matching_word.form.lower() == u'vos' or matching_word.form.lower() == u'tú' or matching_word.form.lower() == u'Ud.'))
                    or
                    ((persona_verbo == '1') and (nro_verbo == 'S') and (matching_word.form.lower() == u'yo'))
                    or ((persona_verbo == '1')
                        and (nro_verbo == 'P')
                        and (matching_word.form.lower() == u'nosotros' or matching_word.form.lower() == u'nosotras'))):
                    self.sujeto = entidad
                    break
                # ojo que acá mezclamos entidad singular con verbo plural
                if (nro_verbo == 'P') and (persona_verbo == '2' or persona_verbo == '1') and (numero == 'P' or numero == 'S'):
                    self.sujeto = entidad
                    break

        # logger.info("verb info %s %s %s" % (persona_verbo, nro_verbo, extra_verbo))
        # logger.info("self.sujeto %s"  % self.sujeto)

        if not self.sujeto:
            max_dist = 1                  # a qué distancia del verbo puede empezar una SN a derecha para ser sujeto
            entidades_a_derecha = filter(lambda x: abs(primer_verbo.words[0].position - x.words[0].position) <= max_dist,
                                         self.entidades_no_sujeto)

            for entidad in entidades_a_derecha:
                nucleo, (label, genero, numero) = entidad.nucleo()
                # logger.info("entidad a derecha: %s %s %s %s" % (nucleo, label, genero, numero))
                if nucleo:
                    matching_word = nucleo.words[0]
                    if (nro_verbo == numero) and persona_verbo == '3':
                        self.sujeto = entidad
                        self.entidades_no_sujeto.remove(entidad)
                        break
                    if (((persona_verbo == '2')
                         and (nro_verbo == 'S')
                         and (matching_word.form.lower() == u'vos' or matching_word.form.lower() == u'tú' or matching_word.form.lower() == u'Ud.'))
                        or ((persona_verbo == '1') and (nro_verbo == 'S') and (matching_word.form.lower() == u'yo'))
                        or ((persona_verbo == '1')
                            and (nro_verbo == 'P')
                            and (matching_word.form.lower() == u'nosotros' or matching_word.form.lower() == u'nosotras'))):
                        self.sujeto = entidad
                        self.entidades_no_sujeto.remove(entidad)
                        break
                    if (nro_verbo == 'P') and (persona_verbo == '2' or persona_verbo == '1') and numero == 'P':
                        self.sujeto = entidad
                        self.entidades_no_sujeto.remove(entidad)
                        break

        if not self.sujeto:
            self.sujeto = sujeto_para(primer_verbo.words[0])
            self.sujeto_es_tacito = True

    def hallar_subordinante(self):
        if self.all.label == 'subord-rel':
            encabezador = self.all.subordinante()
            if encabezador: self.subordinante = encabezador

    def hallar_SVO(self):
        svo = self.svo # SVO()

        if not(self.verbs):
            svo.build()
            self.svo = svo
            return

        if self.modal: svo.modal_verb = self.modal

        primer_verbo = sorted(set(self.verbs), key=lambda x: x.start)[0]
        lemma = primer_verbo.words[0].lemma
        if scripts_verbales.has_key(lemma):
            if self.contiene_global_operator:
                marco_verbal = 'N'
            else:
                marco_verbal = scripts_verbales[lemma]
        else:
            marco_verbal = 'N'

        svo.verb = Verb(primer_verbo, marco_verbal)

        if self.sujeto: svo.subject = SVOelement(self.sujeto)

        sns_incluidas = self.entidades_sujeto + self.entidades_no_sujeto

        # if not sns_incluidas:
        #     svo.build()
        #     self.svo = svo
        #     return

        # if not svo.subject:
        #     sujetos = filter(lambda e: e.end < svo.verb.verb.start, sns_incluidas)
        #     if sujetos: svo.subject = SVOelement(sujetos[0])

        if self.all.label in ['grup-verb', 'verb-pass']:
            subnivel_hijez_directa = 1
        else:
            subnivel_hijez_directa = 2

        # regla 1: no_sujeto sin encabezador 'a', a nivel de hijo directo de grup-verb
        no_sujetos_sns = filter(lambda e: e.start > svo.verb.verb.end and e.__str__() != svo.subject.__str__(), sns_incluidas)
        # (más sujetos_sns que no hayan sido usados para llenar self.sujeto)
        no_sujetos_sns.extend(filter(lambda e: e.start < svo.verb.verb.end and e.__str__() != svo.subject.__str__(), sns_incluidas))
        candidatos_objeto = filter(lambda x: x.nivel == self.all.nivel + subnivel_hijez_directa, no_sujetos_sns)
        # logger.info("candidatos objeto: %s" % [x.__str__() for x in candidatos_objeto])
        # logger.info("sujeto: %s" % svo.subject.__str__())
        if candidatos_objeto: svo.object = SVOelement(candidatos_objeto[0])

        sps   = self.by_label('grup-sp')

        # regla 2: no_sujeto con encabezador 'a', a nivel de hijo directo de grup-verb
        candidatos_objeto = filter(lambda x: x.nivel == self.all.nivel + subnivel_hijez_directa and x.words[0].lemma == 'a', sps)
        if candidatos_objeto and not svo.object:
            sn_en_sp = filter(lambda c: c.label == 'sn', candidatos_objeto[0].children)
            if sn_en_sp: svo.object = SVOelement(sn_en_sp[0])

        # regla 3: si es patons con tag PP[123][CF][NSP][A0]XX, es objeto
        # patons = filter(lambda sn: sn.label == 'patons', sns_incluidas)
        # if patons and not svo.object:
        #     candidatos_objeto = filter(lambda p: re.match(r'PP[123][CF][NSP][A0]..', p.words[0].tag, re.U), patons)
        #     tag = candidatos_objeto[0].words[0].tag
        #     match = re.match(r'PP([123])([CF])([NSP])[A0]..', tag, re.U)
        #     persona, genero, numero = match.group(1), match.group(2), match.group(3)
        #     form = pronombres_objeto[(persona, genero, numero)]
        #     position = candidatos_objeto[0].words[0].position
        #     w = u'+(%s %s %s -){%d' % (form, form, tag, position)
        #     svo.object = SVOelement(Estructura((position-1, position+1, ['pronombre_[', w, ']'], 1)))
        #     logger.info("patons candidato: %s -> form: %s" % (candidatos_objeto[0], w))

        if self.entidades_privativa: svo.privativa = [SVOelement(entidad_privativa) for entidad_privativa in self.entidades_privativa]

        # regla 4: si no es objeto, es adjunto
        if svo.object:
            svo.others = [SVOelement(x) for x in filter(lambda o: svo.object.estructura.__str__() != o.__str__()
                                                        and not(svo.object.estructura.contains(o)), no_sujetos_sns)]
        else:
            svo.others = [SVOelement(x) for x in no_sujetos_sns]

        # quitar adjuntos que contengan algo que duplique lo que haya en alguna Eprivativa
        valid_others = []
        privativas_sin_encabezador = [' '.join([w.__str__() for w in p.estructura.words[1:]]) for p in svo.privativa]
        if svo.others and svo.privativa:
            for o in svo.others:
                for pse in privativas_sin_encabezador:
                    # if unidecode.unidecode(o.estructura.__str__().decode('utf-8')).find(unidecode.unidecode(pse)) == -1: valid_others.append(o)
                    if o.estructura.__str__().find(pse) == -1: valid_others.append(o)
        svo.others = valid_others

        sadvs = self.by_label('sadv')
        # logger.info("sadvs: %s", ' - '.join([sadv.__str__() for sadv in sadvs]))

        # regla 5: agregar adverbios
        if sadvs:
            svo.adverbs = [SVOelement(sadv) for sadv in sadvs]

        # regla 6: si es pasiva, mover sujeto a objeto (pisando objeto)
        if self.pasiva and svo.subject:
            svo.object = SVOelement(svo.subject.estructura)
            svo.subject = SVOelement()

        # done
        svo.build()
        self.svo = svo
        return
