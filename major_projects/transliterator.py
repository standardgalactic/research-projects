import logging
from nltk.corpus import cmudict
from mappings import PHONEME_TO_ARABIC, COMMON_OVERRIDES
from utils import tokenize_text, clean_phoneme

cmu_dict = cmudict.dict()
logging.basicConfig(filename="transliterator.log", level=logging.INFO)

def get_phonemes(word):
    word_lower = word.lower()
    if word_lower in cmu_dict:
        return cmu_dict[word_lower][0]
    logging.warning(f"No phonemes for '{word}', fallback to spelling.")
    return list(word.upper())

def transliterate_phoneme(p):
    p_clean = clean_phoneme(p)
    ar_tuple = PHONEME_TO_ARABIC.get(p_clean)
    if ar_tuple:
        letter, diacritic = ar_tuple
        return (letter or '') + (diacritic or '')
    logging.warning(f"Unknown phoneme '{p}'")
    return ''

def transliterate_word(word):
    word_lower = word.lower()
    if word_lower in COMMON_OVERRIDES:
        return COMMON_OVERRIDES[word_lower]
    phonemes = get_phonemes(word)
    return ''.join(transliterate_phoneme(p) for p in phonemes)

def transliterate_text(text):
    return ''.join(transliterate_word(w) if w.isalpha() else w for w in tokenize_text(text))
