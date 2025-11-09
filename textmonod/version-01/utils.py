import difflib
from typing import List, Tuple

def align_tokens(prev: List[str], curr: List[str]) -> Tuple[int,int,int]:
    sm = difflib.SequenceMatcher(None, prev, curr)
    new = sum(b2-b1 for tag,a1,a2,b1,b2 in sm.get_opcodes() if tag=='insert')
    keep = sum(a2-a1 for tag,a1,a2,b1,b2 in sm.get_opcodes() if tag in ('equal','replace'))
    length = len(prev)
    return new, keep, length

def tokenize(text: str) -> List[str]:
    return text.split()