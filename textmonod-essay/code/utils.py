from difflib import SequenceMatcher
def token_diff(v_prev, v_curr):
    m = SequenceMatcher(None, v_prev, v_curr)
    new, retained = 0, 0
    for tag,i1,i2,j1,j2 in m.get_opcodes():
        if tag=='equal': retained+=i2-i1
        if tag=='insert': new+=j2-j1
    return new, retained, len(v_prev)
