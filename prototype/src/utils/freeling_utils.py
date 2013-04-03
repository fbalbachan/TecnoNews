#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

host        = open('freeling_config/host', 'r').read().strip('\n').strip('FREELING_HOST=')
client      = open('freeling_config/client', 'r').read().strip('\n').strip('FREELING_CLIENT=')
parser_port = open('freeling_config/parser_port', 'r').read().strip('\n').strip('FREELING_PARSER_PORT=')
tagger_port = open('freeling_config/tagger_port', 'r').read().strip('\n').strip('FREELING_TAGGER_PORT=')

class FreelingAnalyzer(object):
    def __init__(self, freeling_host=host, freeling_client=client, freeling_parser_port=parser_port, freeling_tagger_port=tagger_port):
        self.host = freeling_host
        self.client = freeling_client
        self.parser_port = freeling_parser_port
        self.tagger_port = freeling_tagger_port

    def parse(self, sentence):
        command = u'echo "%s." | ' + self.client + ' ' + self.host + ':' + self.parser_port
        pretty_output = [s.decode('utf-8') for s in os.popen((command % sentence).encode('utf-8')).read().split('\n')]
        print pretty_output
        output = [s.strip() for s in os.popen((command % sentence).encode('utf-8')).read().split('\n')]
        print output
        return output, pretty_output

    def tag(self, sentence):
        command = u'echo "%s." | ' + self.client + ' ' + self.host + ':' + self.tagger_port
        output = [s.decode('utf-8').strip() for s in os.popen((command % sentence).encode('utf-8')).read().split('\n')]
        return output
