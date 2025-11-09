import streamlit as st
from curator import route_memory
import json

st.title("RAG Curator — Demo UI")
content = st.text_area("Paste memory text", height=200)
phase = st.selectbox("Project phase", ["discovery","preservation","distillation","deployment","maintenance"])
if st.button("Route"):
    rec = route_memory(content or "Test: what if we combine X and Y?", phase=phase)
    st.json(rec)
    st.markdown("**Primary Owner:** "+rec["routing"]["primary_owner"])
    st.markdown("**Weights:**")
    st.write(rec["routing"]["weights"])
