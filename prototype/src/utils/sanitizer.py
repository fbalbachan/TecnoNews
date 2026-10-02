#-*- coding: utf-8 -*-
import re
from src.decorators.singleton import singleton
from src.utils.languageFilter import LanguageFilter
from src.utils.configProvider import ConfigProvider


@singleton
class Sanitizer():
    def __init__(self):

        self.config = ConfigProvider()
        self.language_filter_status = self.config.get('language_filter', 'status')
        self.paragraph_to_avoid = self._load_banned_paragraphs()
        self.language_filter = None


    def upper_repl(self, match):
        return match.group(1).upper()

    def post_process(self, text_content):
        if not isinstance(text_content, str):
            text_content = str(text_content, 'utf-8')
        new_content = text_content

        re1 = re.compile(r'\bde\b \bel\b', re.UNICODE)
        new_content = re.sub(re1, 'del', new_content)
        re1 = re.compile(r'\bDe\b \bel\b', re.UNICODE)
        new_content = re.sub(re1, 'Del', new_content)

        re1 = re.compile(r'\ba\b \bel\b', re.UNICODE)
        new_content = re.sub(re1, 'al', new_content)
        re1 = re.compile(r'\bA\b \bel\b', re.UNICODE)
        new_content = re.sub(re1, 'Al', new_content)

        re1 = re.compile(r'\by\b \b(i|I|hi)', re.UNICODE)
        new_content = re.sub(re1, r'e \1', new_content)
        re1 = re.compile(r'\bY\b \b(i|I|hi)', re.UNICODE)
        new_content = re.sub(re1, r'E \1', new_content)

        re1 = re.compile(r'\be\b (\b[^iI])', re.UNICODE)
        new_content = re.sub(re1, r'y \1', new_content)
        re1 = re.compile(r'\bE\b (\b[^iI])', re.UNICODE)
        new_content = re.sub(re1, r'Y \1', new_content)

        re1 = re.compile(r'\bu\b (\b[^oO])', re.UNICODE)
        new_content = re.sub(re1, r'o \1', new_content)
        re1 = re.compile(r'\bU\b (\b[^oO])', re.UNICODE)
        new_content = re.sub(re1, r'O \1', new_content)

        re1 = re.compile(r'\bo\b \b(o|O|ho|Ho)', re.UNICODE)
        new_content = re.sub(re1, r'u \1', new_content)
        re1 = re.compile(r'\bO\b \b(o|O|ho|Ho)', re.UNICODE)
        new_content = re.sub(re1, r'U \1', new_content)

        re1 = re.compile(r'\bdela\b', re.UNICODE)
        new_content = re.sub(re1, 'de la', new_content)
        re1 = re.compile(r'\bDela\b', re.UNICODE)
        new_content = re.sub(re1, 'De la', new_content)

        re1 = re.compile(r'([.,?!;_-])[,?!;_-]', re.UNICODE)
        new_content = re.sub(re1, r'\1', new_content)

        re1 = re.compile(r'(^\s*[a-zñáéíóú])', re.MULTILINE | re.UNICODE)
        new_content = re.sub(re1, self.upper_repl, new_content)

        return new_content



    def process_content(self, content):
        # We have doubts about the stability of language Filter, so we instanciate each time
        self.language_filter = LanguageFilter()

        # Becouse we have a mixed encodes in pipeline be shure it is unicode
        if not isinstance(content, str):
            content = str(content, 'utf-8')

        new_content = '\n'.join([paragraph for paragraph in content.split('\n')
                                 if not any(x == paragraph[:len(x)] for x in self.paragraph_to_avoid)])

        new_content = re.sub('\(CNN( Español ?)?\) ?(-|–)?', '', new_content)
        new_content = re.sub('\(CNNMoney\) ?(-|–)?', '', new_content)

        modified = True
        while modified:
            modified = False
            words = new_content.split()
            if len(words) > 0:
                words[0] = re.sub('^[A-ZÁÉÍÓÚÑÂÊÎÔÛÇÈËÀÃÜÙÌÕÒ)(_-]{2,}$', '', words[0])
                if "(" in words[0] and ")" in words[0]:
                    words[0] = ""

                if words[0] == "":
                    modified = True
                    new_content = ' '.join(words)



        if self.language_filter_status == 'ON':
            new_content = self.language_filter.only_spanish_paragraph(new_content)

        new_content = re.sub('No te pierdas el v\xeddeo!', '', new_content)

        re.sub(r'a EL PAÍS|a EL PAIS',  'al diario El País de España',
                   new_content, flags=re.UNICODE)

        new_content = re.sub(', enviad(a|o) especial de euronews\.', '', new_content)

        new_content = re.sub(r'(La|El) enviad(a|o) especial de euronews(\ a\ la\ zona)?,',
                             '', new_content)

        new_content = re.sub('a CNN', 'al medio estadounidense CNN', new_content)
        new_content = re.sub('A CNN', 'Al medio estadounidense CNN', new_content)

        return new_content.strip()

    def _load_banned_paragraphs(self):
        """
        load resource of inital substrings to ignore

        :return: list of initial substrings to ignore in pipeline process
        """
        string_paragraphs = []
        paragraphs_filename = self.config.get("resources", "marks_to_avoid_paragraphs")

        for line in open(paragraphs_filename, 'r', encoding="utf-8"):
            if line[0] not in ['<', '%', '\n']:
                line_to_add = line.rstrip('\n')
                string_paragraphs.append(line_to_add)

        return string_paragraphs
