import json, sys, numpy as np
from sentence_transformers import SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")
for path in sys.argv[1:]:
    d=json.load(open(path))
    vec=model.encode(d.get("summary",d.get("text",""))[:8000],normalize_embeddings=True)
    np.save(path.replace(".memory",".vector"),vec)
    d["embedding_ready"]=True
    json.dump(d,open(path,"w"),indent=2)
