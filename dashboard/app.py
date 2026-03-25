# dashboard/app.py
import sys
import os
from pathlib import Path
import time
import torch  # add this at the top with your imports
# -----------------------------
# Path Fix
# -----------------------------
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -----------------------------
# Imports
# -----------------------------
import streamlit as st
from app.services import QASystem
from pypdf import PdfReader
import docx

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="RAG Document Assistant", layout="wide")

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
.chat-user {
    background-color: #DCF8C6;
    color: #000;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    text-align: right;
}

.chat-assistant {
    background-color: #262730;
    color: #FFFFFF;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Better contrast for dark/light mode */
body {
    color: #FFFFFF;
}

.model-badge {
    background-color: #111;
    color: #0f0;
    padding: 6px 10px;
    border-radius: 8px;
    display: inline-block;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# MODEL FETCH
# =========================
from itertools import islice

# =========================
# MODEL FETCH (CACHED)
# =========================
# =========================
# MODEL FETCH (CACHED)
# =========================
@st.cache_data(show_spinner=False)
def fetch_models(provider, api_key):
    """
    Fetch top 5 models for a given provider (HF, Cohere, OpenAI)
    HF uses curated, compatible models only (preselected)
    Cohere/OpenAI fetch dynamically and validate API key
    """
    provider = provider.lower()

    def safe_str(x):
        if x is None:
            return ""
        return str(x).encode("utf-8", errors="ignore").decode("utf-8")

    # ---------------------
    # HUGGING FACE (curated)
    # ---------------------
    if provider == "hf":
        hf_models = [
            {"id": "tiiuae/falcon-7b-instruct", "desc": "HF • instruct (medium)"},
            {"id": "TheBloke/wizardLM-7B-GPTQ", "desc": "HF • conversational"},
            {"id": "bigscience/bloom-560m", "desc": "HF • text-generation (small)"},
            {"id": "EleutherAI/gpt-neo-125M", "desc": "HF • text-generation (tiny)"},
            {"id": "facebook/opt-125m", "desc": "HF • text-generation (tiny)"}
        ]
        return hf_models

    # ---------------------
    # COHERE (dynamic)
    # ---------------------
    elif provider == "cohere":
        import cohere
        client = cohere.Client(api_key)

        try:
            # Quick API check
            resp = client.chat(model="command-r-08-2024", message="hi", max_tokens=1)
            _ = safe_str(getattr(resp, "text", "") or getattr(resp, "message", ""))
        except Exception as e:
            raise RuntimeError(f"Cohere API error: {safe_str(e)}")

        # Return top 5 recommended
        return [
            {"id": "command-r-08-2024", "desc": "Fast chat (free)"},
            {"id": "command-xlarge-nightly", "desc": "Large generation"},
            {"id": "tiny-aya-fire", "desc": "Lightweight free"},
            {"id": "command-a-reasoning-08-2025", "desc": "Reasoning"},
            {"id": "command-r7b", "desc": "Multilingual"}
        ]

    # ---------------------
    # OPENAI (dynamic)
    # ---------------------
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        try:
            _ = client.models.list()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {safe_str(e)}")

        return [
            {"id": "gpt-4o-mini", "desc": "Best free-tier"},
            {"id": "gpt-3.5-turbo", "desc": "Fast & cheap"},
            {"id": "gpt-4", "desc": "High quality"},
            {"id": "gpt-4-32k", "desc": "Long context"},
            {"id": "gpt-3.5-turbo-16k", "desc": "Long context"}
        ]

    return []

# =========================
# HF MODEL COMPATIBILITY CHECK
# =========================
def check_hf_model_task(selected_model_id, hf_models, required_task="text-generation"):
    """
    Ensure the selected HF model supports the task you need.
    """
    model = next((m for m in hf_models if m["id"] == selected_model_id), None)
    if not model:
        raise RuntimeError(f"Model {selected_model_id} not found")
    if model["task"] != required_task:
        raise RuntimeError(f"Model {selected_model_id} does not support task '{required_task}'")
    return True
# =========================
# HEADER
# =========================
st.title("📄 RAG Document Assistant")

# =========================
# SESSION STATE
# =========================
if "qa_system" not in st.session_state:
    st.session_state.qa_system = QASystem()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm_ready" not in st.session_state:
    st.session_state.llm_ready = False

if "doc_ready" not in st.session_state:
    st.session_state.doc_ready = False

if "models" not in st.session_state:
    st.session_state.models = []

if "api_valid" not in st.session_state:
    st.session_state.api_valid = False


# =========================
# SIDEBAR
# =========================
# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Setup")

    # Reset
    if st.button("🔄 Reset System"):
        st.session_state.clear()
        st.rerun()

    # Provider
    provider = st.selectbox("Choose LLM Provider", ["hf", "openai", "cohere"])

    # API Key
    api_key = st.text_input("Enter API Key", type="password")

    selected_model = None
    if api_key:
        if st.button("🔍 Load Available Models"):
            with st.spinner("Fetching models..."):
                try:
                    models = fetch_models(provider, api_key)
                    st.session_state.models = models
                    st.session_state.api_valid = True
                    st.success("✅ Models Loaded")
                except Exception as e:
                    st.session_state.models = []
                    st.session_state.api_valid = False
                    st.error(f"❌ API Error: {e}")
    else:
        st.info("Enter API key to load models")

    # Model Selection
    if st.session_state.api_valid and st.session_state.models:
        device_type = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Device detected: {device_type.upper()}")

        # GPU-aware model display
        display_models = []
        for m in st.session_state.models:
            if provider == "hf" and device_type == "cpu" and any(x in m["desc"].lower() for x in ["7b", "8b"]):
                display_models.append(f"{m['id']} — {m['desc']} ⚠️ CPU heavy")
            else:
                display_models.append(f"{m['id']} — {m['desc']}")

        selected_label = st.selectbox("Select Model", display_models)
        selected_model = selected_label.split(" — ")[0]

        st.markdown(f'<div class="model-badge">{provider.upper()} | {selected_model}</div>', unsafe_allow_html=True)

    # Temperature
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7)

    # Initialize LLM
    if st.button("🚀 Initialize LLM"):
        if not api_key:
            st.error("Enter API key first")
        elif not selected_model:
            st.error("Select a model")
        else:
            try:
                st.session_state.qa_system.set_llm(
                    provider=provider,
                    api_key=api_key,
                    temperature=temperature,
                    model=selected_model
                )
                st.session_state.qa_system.llm.invoke("Hello")
                st.session_state.llm_ready = True
                st.success("✅ LLM Is Ready")
            except Exception as e:
                st.error(f"❌ Init failed: {e}")

    st.divider()

    # Upload document
    if not st.session_state.llm_ready:
        st.warning("Initialize LLM first")
    else:
        uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"])
        if uploaded_file and st.button("⚡ Process Document"):
            with st.spinner("Processing document..."):
                if uploaded_file.name.endswith(".pdf"):
                    reader = PdfReader(uploaded_file)
                    text = "\n".join([p.extract_text() or "" for p in reader.pages])
                else:
                    doc = docx.Document(uploaded_file)
                    text = "\n".join([p.text for p in doc.paragraphs])
                st.session_state.qa_system.build_index(text)
                st.session_state.doc_ready = True
            st.success("✅ Document Is Ready")

    # Clear Chat
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []

# =========================
# STATUS BAR
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("LLM", "Ready" if st.session_state.llm_ready else "Not Ready")

with col2:
    st.metric("Document", "Loaded" if st.session_state.doc_ready else "Not Loaded")

with col3:
    st.metric("Messages", len(st.session_state.messages))


# =========================
# AUTO LOAD INDEX
# =========================
if not st.session_state.doc_ready and getattr(st.session_state.qa_system, "vectorstore", None):
    st.session_state.doc_ready = True


# =========================
# CHAT
# =========================
if st.session_state.doc_ready:

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

    query = st.chat_input("Ask a question about your document...")

    if query:
        if not st.session_state.llm_ready:
            st.warning("Initialize LLM first")
        else:
            st.session_state.messages.append({"role": "user", "content": query})

            st.markdown(f'<div class="chat-user">{query}</div>', unsafe_allow_html=True)

            with st.spinner("Thinking..."):
                docs = st.session_state.qa_system.retrieve(query)

                context = "\n\n".join([d.page_content for d in docs])

                prompt = f"""
Answer based on the context below.

Context:
{context}

Question: {query}

Answer:
"""

                response_placeholder = st.empty()
                full_response = ""

                # ✅ REAL STREAMING
                for chunk in st.session_state.qa_system.llm.stream(prompt):
                    full_response += chunk
                    response_placeholder.markdown(
                        f'<div class="chat-assistant">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )

                # Final render
                response_placeholder.markdown(
                    f'<div class="chat-assistant">{full_response}</div>',
                    unsafe_allow_html=True
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

            # Sources
            with st.expander("📚 Sources"):
                for i, doc in enumerate(docs):
                    st.markdown(f"**Chunk {i+1}:**")
                    st.write(doc.page_content[:500] + "...")

else:
    st.warning("Upload and process a document to start chatting.")