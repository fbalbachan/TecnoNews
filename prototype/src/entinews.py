# -*- coding: utf-8 -*-

from model.sentence import *
from model.sentenceSplitter import *
from utils.logger_utils import *


class Entinews:
	def sentences_for(self, text):
		logger = self.logger
		logger.info('.' * 80)
		logger.info("new text: %s" % text)

		sentenceSplitter = SentenceSplitter()
		sentences = sentenceSplitter.sentences_in(text)

		resultsByIndex = []

		sentenceNumber = 0

		for sentence in sentences:
			sentenceNumber = sentenceNumber + 1
			logger.info(sentence.evidence)
			logger.info(sentence)

			resultByIndex = sentenceNumber, self.result_for(sentence)
			resultsByIndex.append(resultByIndex)

		return resultsByIndex

	def result_for(self, sentence):
		result = {}
		result['input_sentence'] = sentence.input_sentence
		result['entities'] = []

		for entity in sentence.entities:
			result['entities'].append({'entity': entity.__str__().decode('utf-8'), 'msi': entity.msi})
			# logger.info(u'result: %s' % result)

		if sentence.verb:
			result['verb'] = sentence.verb_final_form.__str__()
			result['verb.msi'] = sentence.verb.msi
			result['verb.transitivity'] = sentence.verb_transitivity
			result['verb.script_class'] = sentence.verb_script_class
		else:
			result['verb'] = None
			result['verb.msi'] = None
			result['verb.transitivity'] = None
			result['verb.script_class'] = None

		result['boxes'] = sentence.boxes

		if sentence.subject:
			result['subject'] = sentence.subject.__str__().decode('utf-8')
			result['subject.msi'] = sentence.subject.msi
			result['subject.entity_type'] = sentence.subject.entity_type
			result['subject.sentiment'] = u"↑ %.2f, ↓ %.2f" % sentence.subject.sentiment
		else:
			result['subject'] = None
			result['subject.msi'] = None
			result['subject.entity_type'] = None
			result['subject.sentiment'] = u" - "

		if sentence.od:
			result['od'] = sentence.od.__str__().decode('utf-8')
			result['od.msi'] = sentence.od.msi
		else:
			result['od'] = None
			result['od.msi'] = None

		if sentence.oi:
			result['oi'] = sentence.oi.__str__().decode('utf-8')
			result['oi.msi'] = sentence.oi.msi
		else:
			result['oi'] = None
			result['oi.msi'] = None

		if sentence.regimen:
			result['regimen'] = sentence.regimen.__str__().decode('utf-8')
			result['regimen.msi'] = sentence.regimen.msi
		else:
			result['regimen'] = None
			result['regimen.msi'] = None

		if sentence.equative:
			result['equative'] = sentence.equative.__str__().decode('utf-8')
			result['equative.msi'] = sentence.equative.msi
		else:
			result['equative'] = None
			result['equative.msi'] = None

		if sentence.adjuncts:
			result['adjuncts'] = ' | '.join([adjunct.__str__().decode('utf-8') for adjunct in sentence.adjuncts])
			result['adjuncts.msi'] = [adjunct.msi for adjunct in sentence.adjuncts]
		else:
			result['adjuncts'] = None
			result['adjuncts.msi'] = None

		return result

	logger = get_logger("Entinews")
