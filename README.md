# Document Assistant-RAG + LLM

A Retrieval-Augmented Generation (RAG) system for document question-answering using multiple LLM providers with a modern Streamlit interface.

## Features

- **Multiple LLM Providers**: Hugging Face, OpenAI, and Cohere with API key validation
- **Document Support**: PDF and DOCX files with robust processing
- **Real-time Streaming**: For supported providers (OpenAI, Cohere)
- **Vector Search**: FAISS-based document indexing with persistence
- **Modern Web Interface**: Clean white-themed Streamlit dashboard
- **API Key Validation**: Real-time validation with clear error messages
- **Multi-Document Support**: Upload and process multiple documents
- **Response Download**: Save chat responses to your device
- **Session Management**: Persistent chat history and system state

## Setup

### Prerequisites

- Python 3.11+ (Python 3.14 has compatibility issues with LangChain)
- Virtual environment
- API keys for your preferred LLM provider

### Installation

1. **Create virtual environment with Python 3.11:**
   ```bash
   py -3.11 -m venv venv311
   venv311\Scripts\activate  # Windows
   # or
   source venv311/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   Create a `.env` file:
   ```
   HF_API_TOKEN=your_huggingface_token
   OPENAI_API_KEY=your_openai_key
   COHERE_API_KEY=your_cohere_key
   ```

### Running the App

```bash
streamlit run dashboard/app.py
```

The app will be available at `http://localhost:8501`

## Usage

1. **Select LLM Provider**: Choose from Hugging Face, OpenAI, or Cohere
2. **Enter API Key**: Provide your API key (validated in real-time)
3. **Load Models**: Click "Load Available Models" to see available options
4. **Initialize LLM**: Select a model and temperature, then click "Initialize LLM"
5. **Upload Documents**: Upload one or multiple PDF/DOCX files
6. **Process Documents**: Click "Process Document" to build the vector index
7. **Ask Questions**: Use the chat interface to ask questions about your documents
8. **Download Responses**: Save your Q&A session to a file

## Architecture

- `dashboard/app.py`: Modern Streamlit web interface with white theme
- `app/services.py`: Core RAG logic, LLM integrations, and vector store management
- `app/main.py`: FastAPI backend (optional)
- `vectorstore_index/`: FAISS vector store persistence
- `venv311/`: Python 3.11 virtual environment

## API Keys & Providers

### Hugging Face
- **Free**: No API key required for basic models
- **Pro**: Get token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- **Models**: DialoGPT, FLAN-T5, GPT-2 (curated for compatibility)

### OpenAI
- **Pricing**: Pay-per-use
- **API Key**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Models**: GPT-4, GPT-3.5-turbo with streaming support

### Cohere
- **Free Tier**: Available
- **API Key**: Get from [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
- **Models**: Command-R series with streaming support

## Development Challenges & Solutions

During the development of this RAG system, several significant technical challenges were encountered and resolved:

### 1. Import Function Not Defined
- **Error**: `NameError: name 'get_llm' is not defined`
- **Context**: API validation function was called but not imported in dashboard module
- **Solution**: Added `get_llm` to imports in `dashboard/app.py` and updated validation logic

### 2. Python Version Compatibility
- **Error**: `ImportError` with Pydantic V1/V2 conflicts in Python 3.14+
- **Context**: LangChain ecosystem compatibility issues with newer Python versions
- **Solution**: Specified Python 3.11.9 in `runtime.txt` and updated dependency versions

### 3. LangChain Import Conflicts
- **Error**: `ModuleNotFoundError` and `ImportError` between old/new LangChain APIs
- **Context**: Breaking changes in LangChain library updates
- **Solution**: Updated all imports to use current LangChain v0.2+ syntax and compatible versions

### 4. Hugging Face Model Deprecation
- **Error**: `HTTPError: 404` for deprecated model endpoints
- **Context**: Many popular HF models were removed or changed
- **Solution**: Curated working models (DialoGPT, FLAN-T5, GPT-2) and added model validation

### 5. API Key Validation Logic
- **Error**: Generic API errors without clear user feedback
- **Context**: Users couldn't distinguish between invalid keys and network issues
- **Solution**: Implemented comprehensive API validation with specific error messages and LLM instantiation testing

## Known Issues & Solutions

### Python 3.14 Compatibility
- **Issue**: LangChain has Pydantic V1 compatibility issues with Python 3.14+
- **Solution**: Use Python 3.11 or 3.12 (recommended: 3.11)

### API Key Validation
- **Issue**: Invalid API keys show clear error messages
- **Solution**: Ensure correct API key format and active subscription

### Document Processing
- **Issue**: Large files may take time to process
- **Solution**: Split large documents or use smaller chunks

### Streaming Support
- **Hugging Face**: Full response (no real streaming)
- **OpenAI/Cohere**: Real-time token streaming

## Troubleshooting

1. **Import Errors**: Ensure Python 3.11+ and all dependencies installed
2. **API Errors**: Verify API keys and account status
3. **Document Processing**: Check file integrity and format
4. **LLM Initialization**: Try different models or providers
5. **Streamlit Issues**: Clear browser cache and restart

## Recent Updates

- ✅ **API Key Validation**: Real-time validation with clear error messages
- ✅ **Modern UI**: Clean white theme with improved UX
- ✅ **Multi-Document Support**: Upload and process multiple files
- ✅ **Response Download**: Save chat sessions to device
- ✅ **Enhanced Error Handling**: Better user feedback and debugging
- ✅ **Package Updates**: Latest compatible versions
- ✅ **Import Fixes**: Resolved LangChain import conflicts
- ✅ **Model Updates**: Working Hugging Face alternatives
- ✅ Added validation for empty documents and queries
- ✅ Enhanced streaming with fallback for non-streaming providers