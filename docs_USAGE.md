# Usage

1. Ensure Ollama is installed and a Granite model is available (e.g., granite3.2:8b).
2. Install Python deps:
   ```
   pip install -r requirements.txt
   ```
   (requirements include: sentence-transformers, tqdm, streamlit, numpy)
3. Put text files in `to_process/` (top-level `.txt`).
4. Run the pipeline:
   ```
   bash scripts/rag_memory_builder.sh to_process
   ```
5. Start the dashboard:
   ```
   export MEMORIES_DIR=to_process/memories
   streamlit run dashboard/app.py
   ```
