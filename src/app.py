"""Streamlit chat UI for the cold-chain dispatch agent."""

import sys
import uuid
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from src.agent import ask  # noqa: E402
from src.rag import get_vectorstore  # noqa: E402

st.set_page_config(page_title="Cold-Chain Dispatch Console", page_icon="🧊", layout="wide")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🧊 Dispatch Console")
    st.caption(f"Model: `{config.DEEPSEEK_MODEL}`")
    st.caption(f"Session: `{st.session_state.thread_id[:8]}`")
    st.divider()
    try:
        st.write(f"📚 SOP chunks in ChromaDB: **{get_vectorstore()._collection.count()}**")
    except Exception as e:
        st.write(f"📚 ChromaDB: not ready ({e})")
    st.write("🔑 DeepSeek key: **set**" if config.DEEPSEEK_API_KEY else "🔑 DeepSeek key: **missing** (see .env)")
    if st.button("🗑️ New session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

st.title("Cold-Chain Incident Control Dashboard")
st.caption("Chat with fleet telemetry, live corridor weather, and SOP compliance.")

for entry in st.session_state.messages:
    with st.chat_message(entry["role"]):
        for step in entry.get("trace", []):
            with st.expander(f"🔧 {step['tool']}", expanded=False):
                st.json(step["args"])
                st.code(step["output"], language="text")
        st.markdown(entry["content"])

question = st.chat_input("Query fleet telemetry, corridor updates, or compliance thresholds...")
if question:
    st.session_state.messages.append({"role": "user", "content": question, "trace": []})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.status("🧠 Agent working...", expanded=True) as status:
            try:
                answer, trace = ask(question, st.session_state.thread_id)
                status.update(label="Done", state="complete", expanded=False)
            except Exception as e:
                answer, trace = f"⚠️ {e}", []
                status.update(label="Failed", state="error", expanded=True)
        for step in trace:
            with st.expander(f"🔧 {step['tool']}", expanded=False):
                st.json(step["args"])
                st.code(step["output"], language="text")
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace})
