
# RAG Cognitive Stack — Repository

This repository contains a production-ready scaffold implementing the five-persona
RAG memory system (Archivist, Formalist, Synthesist, Strategist, Curator) plus
routing, ontology tagging, benchmarks, UI, Dockerization, tests, and a LaTeX paper.

**Contents**
- `memory_routing_schema.json` — JSON Schema for memory routing records.
- `prompts.py` — Persona prompt templates.
- `curator.py` — routing implementation and curator logic (simulated LLM).
- `ontology.py` — vector tagging ontology.
- `tagger.py` — stub for embedding tagging projection.
- `route_tests.py` — pytest suite for routing.
- `benchmark.py` — synthetic failure-mode benchmark.
- `app.py` — minimal Streamlit UI for adding memories and seeing routing.
- `samples/` — example `.memory` files.
- `Dockerfile` and `docker-compose.yml` — containerization.
- `main.tex` — LaTeX paper draft.
- `requirements.txt` — Python dependencies.

**Usage (development)**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

**Notes**
- LLM calls are stubbed/simulated. Replace the TODO markers in `curator.py` with real LLM calls (OpenAI/Anthropic/local).
- Embedding projection functions in `tagger.py` are placeholders; integrate your vector model (sentence-transformers or cloud embeddings) and train regressors to map embeddings to ontology scores.

