import unittest
from transliterator import transliterate_text, transliterate_word

class TestTransliteration(unittest.TestCase):

    def test_common_words(self):
        self.assertEqual(transliterate_word("the"), 'ذَا')
        self.assertEqual(transliterate_word("to"), 'تُو')
        self.assertEqual(transliterate_word("a"), 'أَ')

    def test_custom_words(self):
        result = transliterate_text("Psychocinema delves into ideology")
        self.assertIn('ك', result)
        self.assertIn('ج', result)

    def test_fallback_unknown(self):
        result = transliterate_text("Flyxion")
        self.assertTrue(len(result) > 0)

    def test_diacritics_present(self):
        result = transliterate_text("capital")
        self.assertRegex(result, r'[َُِ]')

if __name__ == '__main__':
    unittest.main()
