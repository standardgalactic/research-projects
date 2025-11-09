import json, subprocess, re, textwrap

def call_ollama(prompt: str, text: str) -> str:
    p = subprocess.Popen(["ollama","run","granite3.2:8b",prompt], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out,_ = p.communicate(text)
    return out

PERSONA_PROMPTS = {
    "archivist": """You are Archivist. Return JSON only.""",
    "formalist": """You are Formalist. Return JSON only.""",
    "synthesist": """You are Synthesist. Return JSON only.""",
    "strategist": """You are Strategist. Return JSON only."""
}

def extract_json(txt):
    m=re.search(r"(\{.*\})",txt,re.S)
    return m.group(1) if m else txt

def analyze_with_persona(p, chunk):
    out=call_ollama(PERSONA_PROMPTS[p]+"\n"+chunk,"")
    try:
        return json.loads(extract_json(out))
    except:
        return {"_raw":out}
