import unittest
from src.utils.sanitizer import Sanitizer


class SanitizerTest(unittest.TestCase):

    def test_clean_mix(self):
        content = open('tests/input/sanitizer_test.text').read()
        self.sanitizer = Sanitizer()
        result = self.sanitizer.process_content(content=content)
        if result:
            print result

        assert not result


if __name__ == '__main__':
    unittest.main()