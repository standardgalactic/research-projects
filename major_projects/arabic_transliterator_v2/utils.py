import re

def tokenize_text(text):
    return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

def clean_phoneme(p):
    return re.sub(r'\d', '', p)
