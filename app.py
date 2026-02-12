import streamlit as st
import requests
import os
import json

# ────────────────────────────────────────────────
#               CONFIGURATION
# ────────────────────────────────────────────────

# Use Streamlit secrets (best & secure way) → set in deployment dashboard
# Fallback: environment variable → fallback: hardcoded (only for local testing!)
API_KEY = st.secrets.get("XAI_API_KEY", os.getenv("XAI_API_KEY", "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"))

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL   = "grok-beta"   # or "grok-3" etc. — check https://docs.x.ai for latest models

# ────────────────────────────────────────────────
#               AI QUERY FUNCTION
# ────────────────────────────────────────────────

def query_grok(question: str) -> str:
    if not API_KEY or API_KEY.startswith("sk-XXX"):
        return "Error: No valid xAI API key found. Set it in Streamlit secrets or as env variable."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert nursing educator and clinical tutor. "
                    "Answer nursing course questions accurately, in detail, using evidence-based information. "
                    "Explain concepts clearly, define medical terms, emphasize patient safety, and use simple language when helpful. "
                    "Structure answers well (use bullet points, numbered lists, tables when appropriate)."
                )
            },
            {"role": "user", "content": question}
        ],
        "temperature": 0.65,
        "max_tokens": 1200
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"API Error: {str(e)}\n\nPlease check your API key and internet connection."

# ────────────────────────────────────────────────
#               STREAMLIT UI
# ────────────────────────────────────────────────

st.set_page_config(page_title="Nursing AI Tutor", page_icon="🩺", layout="wide")

st.title("🩺 Nursing Course AI Tutor")
st.markdown("Ask any question about anatomy, physiology, pharmacology, patient care, NCLEX-style questions, procedures, ethics, etc.")

# Chat-like interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your nursing question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_grok(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar extras
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by xAI Grok • For educational use • Always verify with textbooks & lecturers")