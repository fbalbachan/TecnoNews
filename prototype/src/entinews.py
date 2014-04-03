# -*- coding: utf-8 -*-

from utils.logger_utils import *
from model import sentenceSplitter
from utils import tokenize
from model.sentence import *

class Entinews:
	def sentences_for(self, text):
		self.logger.info('.'*80)
		self.logger.info("new text: %s" % text)

		#logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)
		input_sentences = sentenceSplitter.splitInSentences(text)

		initially_processed_sentences = [tokenize.replace_repeated_letters(tokenize.limpieza_inicial(tokenize.detroll(s))) for s in input_sentences]

		sentencesResults = []

		sentenceNumber = 0

		for sentenceText in initially_processed_sentences:

			sentenceNumber = sentenceNumber + 1

		 	sentence = Sentence(sentenceText)
			print sentence.evidence
			print sentence

			result = {}
			result['input_sentence'] = sentence.input_sentence
			result['sentence_number'] = sentenceNumber
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

			sentencesResults.append(result)

		return sentencesResults
		# return json.dumps(result, ensure_ascii=False).encode('utf-8')
		# return web.template.render().entinews(sentencesResults, text)
		# return page(result)
	logger = get_logger("Entinews")