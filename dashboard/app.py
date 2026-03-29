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
from app.services import QASystem, get_llm
from pypdf import PdfReader
import docx

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="RAG Document Assistant", layout="wide")

# =========================
# CUSTOM CSS - MODERN WHITE THEME
# =========================
st.markdown("""
<style>
/* Modern White Theme */
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --background-color: #ffffff;
    --surface-color: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
}

/* Main container */
.main {
    background-color: var(--background-color);
    color: var(--text-primary);
}

/* Sidebar */
.sidebar .sidebar-content {
    background-color: var(--surface-color);
    border-right: 1px solid var(--border-color);
}

/* Headers */
h1, h2, h3 {
    color: var(--text-primary);
    font-weight: 600;
}

/* Buttons */
.stButton button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton button:hover {
    background-color: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Input fields */
.stTextInput input, .stSelectbox select, .stSlider div {
    border: 2px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 12px;
    background-color: var(--background-color);
    color: var(--text-primary);
}

.stTextInput input:focus, .stSelectbox select:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* Chat messages - Modern design */
.chat-user {
    background: linear-gradient(135deg, var(--primary-color), #3b82f6);
    color: white;
    padding: 16px 20px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    text-align: right;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
    max-width: 80%;
    margin-left: auto;
    word-wrap: break-word;
}

.chat-assistant {
    background-color: var(--surface-color);
    color: var(--text-primary);
    padding: 16px 20px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    max-width: 80%;
    word-wrap: break-word;
}

/* Status badges */
.model-badge {
    background: linear-gradient(135deg, var(--success-color), #34d399);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

/* Metrics */
.metric-container {
    background-color: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary-color);
}

.metric-label {
    font-size: 14px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* File uploader */
.uploadedFile {
    background-color: var(--surface-color);
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s ease;
}

.uploadedFile:hover {
    border-color: var(--primary-color);
    background-color: rgba(37, 99, 235, 0.02);
}

/* Success/Error messages */
.success-message, .error-message, .warning-message {
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
    font-weight: 500;
}

.success-message {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.error-message {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--error-color);
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.warning-message {
    background-color: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
    border: 1px solid rgba(245, 158, 11, 0.2);
}

/* Expander */
.streamlit-expanderHeader {
    background-color: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 500;
}

.streamlit-expanderContent {
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 16px;
}

/* Chat input */
.stChatInput input {
    border: 2px solid var(--border-color);
    border-radius: 24px;
    padding: 12px 20px;
    background-color: var(--background-color);
    color: var(--text-primary);
}

.stChatInput input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* Download buttons */
.download-button {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.download-button:hover {
    background-color: #475569;
    transform: translateY(-1px);
}

/* Spinner */
.spinner {
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 768px) {
    .chat-user, .chat-assistant {
        max-width: 95%;
    }

    .metric-container {
        margin-bottom: 12px;
    }
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
        # Validate API key with a quick test
        try:
            llm = get_llm("hf", api_key, "gpt2", temperature=0.0, max_tokens=1)
            _ = llm.invoke("hi")
        except Exception as e:
            raise RuntimeError(f"Hugging Face API error: {safe_str(e)}")

        hf_models = [
            {"id": "microsoft/DialoGPT-medium", "desc": "HF • conversational (medium)"},
            {"id": "distilbert-base-uncased", "desc": "HF • text-generation (small)"},
            {"id": "google/flan-t5-small", "desc": "HF • instruct (small)"},
            {"id": "microsoft/DialoGPT-small", "desc": "HF • conversational (tiny)"},
            {"id": "gpt2", "desc": "HF • text-generation (tiny)"}
        ]
        return hf_models

    # ---------------------
    # COHERE (dynamic)
    # ---------------------
    elif provider == "cohere":
        import cohere
        client = cohere.Client(api_key)

        try:
            # Quick API check using get_llm
            llm = get_llm("cohere", api_key, "command-r-08-2024", temperature=0.0, max_tokens=1)
            _ = llm.invoke("hi")
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
            # Quick API check using get_llm
            llm = get_llm("openai", api_key, "gpt-4o-mini", temperature=0.0, max_tokens=1)
            _ = llm.invoke("hi")
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

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []


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
            st.error("❌ Enter API key first")
        elif not selected_model:
            st.error("❌ Select a model first")
        else:
            with st.spinner("Initializing LLM..."):
                try:
                    st.session_state.qa_system.set_llm(
                        provider=provider,
                        api_key=api_key,
                        temperature=temperature,
                        model=selected_model
                    )
                    # Test the LLM with a simple message
                    test_response = st.session_state.qa_system.llm.invoke("Hello")
                    if test_response and len(test_response.strip()) > 0:
                        st.session_state.llm_ready = True
                        st.success("✅ LLM Is Ready")
                    else:
                        st.error("❌ LLM test failed - empty response")
                except Exception as e:
                    st.session_state.llm_ready = False
                    st.error(f"❌ Init failed: {str(e)}")
                    st.info("💡 Check your API key and try a different model if the issue persists")

    st.divider()

    # Upload documents (Multi-document support)
    if not st.session_state.llm_ready:
        st.warning("⚠️ Initialize LLM first")
    else:
        uploaded_files = st.file_uploader(
            "📄 Upload PDF/DOCX Documents (Multiple files supported)",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files and st.button("⚡ Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    all_texts = []
                    processed_files = []

                    for uploaded_file in uploaded_files:
                        if uploaded_file.name.endswith(".pdf"):
                            reader = PdfReader(uploaded_file)
                            if len(reader.pages) == 0:
                                st.warning(f"⚠️ {uploaded_file.name} appears to be empty")
                                continue
                            text = "\n".join([p.extract_text() or "" for p in reader.pages])
                        else:  # DOCX
                            doc = docx.Document(uploaded_file)
                            text = "\n".join([p.text for p in doc.paragraphs])

                        if not text or len(text.strip()) < 10:
                            st.warning(f"⚠️ {uploaded_file.name} appears to be empty or contains no readable text")
                            continue

                        all_texts.append(text)
                        processed_files.append(uploaded_file.name)

                    if not all_texts:
                        st.error("❌ No valid documents were processed")
                    else:
                        # Build index with all documents
                        st.session_state.qa_system.build_index(all_texts)
                        st.session_state.doc_ready = True
                        st.session_state.processed_files = processed_files

                        total_chars = sum(len(text) for text in all_texts)
                        st.success(f"✅ {len(processed_files)} document(s) processed successfully ({total_chars} characters total)")

                        # Show processed files
                        with st.expander("📋 Processed Files"):
                            for i, filename in enumerate(processed_files, 1):
                                st.write(f"{i}. {filename}")

                except Exception as e:
                    st.error(f"❌ Document processing failed: {str(e)}")
                    st.info("💡 Try different files or check if documents are corrupted")

    # Clear Chat
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []

    # Download full conversation
    if st.session_state.messages:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            conversation_text = "\n\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])
            st.download_button(
                label="📥 Download Full Chat",
                data=conversation_text,
                file_name="full_conversation.txt",
                mime="text/plain",
                key="download_full_conversation",
                help="Download the complete conversation history"
            )

# =========================
# STATUS BAR
# =========================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    status = "✅ Ready" if st.session_state.llm_ready else "❌ Not Ready"
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{status.split()[0]}</div>
        <div class="metric-label">LLM Status</div>
        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">{status.split()[1]}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    doc_count = len(st.session_state.processed_files) if st.session_state.doc_ready else 0
    status = "✅ Loaded" if st.session_state.doc_ready else "❌ Not Loaded"
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{doc_count}</div>
        <div class="metric-label">Documents</div>
        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">{status.split()[1]}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    msg_count = len(st.session_state.messages)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{msg_count}</div>
        <div class="metric-label">Messages</div>
        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Total</div>
    </div>
    """, unsafe_allow_html=True)


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
            st.warning("⚠️ Initialize LLM first")
        elif not query.strip():
            st.warning("⚠️ Please enter a question")
        else:
            st.session_state.messages.append({"role": "user", "content": query})

            st.markdown(f'<div class="chat-user">{query}</div>', unsafe_allow_html=True)

            with st.spinner("🤔 Thinking..."):
                try:
                    # Check if this is a casual conversation or document-related question
                    casual_keywords = [
                        "hi", "hello", "hey", "how are you", "what's up", "good morning",
                        "good afternoon", "good evening", "thanks", "thank you", "bye",
                        "goodbye", "see you", "how do you work", "what can you do",
                        "help", "about you", "who are you"
                    ]
                    is_casual = (
                        any(keyword in query.lower() for keyword in casual_keywords) or
                        len(query.split()) < 4 or
                        query.lower().strip() in ["hi", "hello", "hey", "hi!", "hello!", "hey!"]
                    )

                    if is_casual:
                        # Direct response for casual conversation
                        if any(word in query.lower() for word in ["hi", "hello", "hey"]):
                            response = "👋 Hello! I'm your RAG Document Assistant. I'm ready to help you with questions about your uploaded documents. What would you like to know?"
                        elif "how are you" in query.lower():
                            response = "🤖 I'm doing great, thank you! I'm here and ready to analyze your documents. What questions do you have about your files?"
                        elif any(word in query.lower() for word in ["thanks", "thank you"]):
                            response = "🙏 You're welcome! Feel free to ask me anything else about your documents."
                        elif any(word in query.lower() for word in ["bye", "goodbye", "see you"]):
                            response = "👋 Goodbye! Have a great day!"
                        elif any(word in query.lower() for word in ["how do you work", "what can you do", "help"]):
                            response = "📚 I analyze your uploaded documents and answer questions based on their content. Just upload some PDF or DOCX files, and I can help you find information, summarize content, or answer specific questions about them!"
                        else:
                            response = "🤔 I'm here to help with questions about your documents. What would you like to know about your uploaded files?"

                        st.markdown(f'<div class="chat-assistant">{response}</div>', unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": response})

                        # Download option for casual responses
                        col1, col2 = st.columns([4, 1])
                        with col2:
                            st.download_button(
                                label="📥 Download",
                                data=response,
                                file_name=f"response_{len(st.session_state.messages)}.txt",
                                mime="text/plain",
                                key=f"download_{len(st.session_state.messages)}"
                            )

                    else:
                        # Document-based Q&A with improved streaming
                        docs = st.session_state.qa_system.retrieve(query)

                        if not docs:
                            response = "❌ I couldn't find relevant information in your documents to answer this question. Try rephrasing it or check if your documents contain the information you're looking for."
                            st.markdown(f'<div class="chat-assistant">{response}</div>', unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            context = "\n\n".join([d.page_content for d in docs])

                            prompt = f"""
Answer based on the context below. Be specific and use the information from the documents.

Context:
{context}

Question: {query}

Answer:
"""

                            # Create a container for the streaming response
                            response_container = st.empty()
                            full_response = ""

                            # Handle streaming based on provider with better UI
                            try:
                                for chunk in st.session_state.qa_system.llm.stream(prompt):
                                    if chunk:  # Only add non-empty chunks
                                        full_response += chunk
                                        response_container.markdown(
                                            f'<div class="chat-assistant">{full_response}▌</div>',
                                            unsafe_allow_html=True
                                        )
                            except AttributeError:
                                # Fallback for providers that don't support streaming
                                full_response = st.session_state.qa_system.llm.invoke(prompt)
                                response_container.markdown(
                                    f'<div class="chat-assistant">{full_response}</div>',
                                    unsafe_allow_html=True
                                )

                            # Final render without cursor
                            response_container.markdown(
                                f'<div class="chat-assistant">{full_response}</div>',
                                unsafe_allow_html=True
                            )

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response
                            })

                            # Download and sources in a nice layout
                            col1, col2 = st.columns([3, 1])
                            with col2:
                                st.download_button(
                                    label="📥 Download Response",
                                    data=full_response,
                                    file_name=f"response_{len(st.session_state.messages)}.txt",
                                    mime="text/plain",
                                    key=f"download_response_{len(st.session_state.messages)}"
                                )

                            # Sources with better formatting
                            with st.expander("📚 Sources & References"):
                                st.markdown(f"**Found {len(docs)} relevant sections:**")
                                for i, doc in enumerate(docs, 1):
                                    st.markdown(f"**Source {i}:**")
                                    # Show a preview of the content
                                    preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                                    st.info(preview)

                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    st.info("💡 Try rephrasing your question or check your API connection")

    # Show message when no documents are uploaded
    if not st.session_state.doc_ready:
        st.info("📄 Upload and process some documents to start asking questions!")