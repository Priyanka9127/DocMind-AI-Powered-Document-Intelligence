import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import os
from prometheus_client import start_http_server, Counter, Histogram
import time

# Metrics Definition
# Streamlit reruns the script on every interaction, so we need to ensure metrics are only registered once
if 'REQUEST_COUNT' not in st.session_state:
    st.session_state.REQUEST_COUNT = Counter('docmind_requests_total', 'Total number of requests to DocMind')
    st.session_state.PROCESSING_TIME = Histogram('docmind_processing_seconds', 'Time spent processing documents')
    st.session_state.LLM_LATENCY = Histogram('docmind_llm_response_seconds', 'Time spent waiting for LLM response')

REQUEST_COUNT = st.session_state.REQUEST_COUNT
PROCESSING_TIME = st.session_state.PROCESSING_TIME
LLM_LATENCY = st.session_state.LLM_LATENCY

# Setup Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Start Prometheus Metrics Server on port 8000
try:
    start_http_server(8000)
except OSError:
    pass # Server already started

# Page configuration
st.set_page_config(
    page_title="DocMind - AI Document Intelligence",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #1e3a5f;
        border-left: 4px solid #4a9eff;
        color: white;
    }
    .user-message strong {
        color: #4a9eff;
    }
    .bot-message {
        background-color: #2d1b3d;
        border-left: 4px solid #b794f6;
        color: white;
    }
    .bot-message strong {
        color: #b794f6;
    }
</style>
""", unsafe_allow_html=True)


def clean_llm_response(response):
    """Clean the LLM response by removing <think> tags and extra whitespace"""
    if "<think>" in response:
        response = response.split("</think>")[-1]
    return response.strip()


def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDF documents"""
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            st.error(f"Error reading {pdf.name}: {str(e)}")
    return text


def get_text_chunks(text):
    """Split text into manageable chunks for processing"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\\n\\n", "\\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    """Create ChromaDB vector store with embeddings"""
    persist_directory = "./chroma_db"
    
    embeddings = OllamaEmbeddings(
        model="deepseek-r1:1.5b",
        base_url=OLLAMA_BASE_URL
    )
    
    collection_name = f"documents_{int(time.time())}"
    
    vectorstore = Chroma.from_texts(
        texts=text_chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    return vectorstore


def get_conversation_chain(vectorstore):
    """Create conversational retrieval chain with DeepSeek LLM"""
    llm = Ollama(
        model="deepseek-r1:1.5b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.7
    )
    
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True
    )
    
    return conversation_chain


def handle_user_input(user_question):
    """Process user questions and display responses"""
    if st.session_state.conversation is None:
        st.warning("⚠️ Please upload and process documents first!")
        return
    
    REQUEST_COUNT.inc()
    with st.spinner("🤔 Thinking..."):
        try:
            start_time = time.time()
            response = st.session_state.conversation({'question': user_question})
            answer = clean_llm_response(response['answer'])
            LLM_LATENCY.observe(time.time() - start_time)
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': answer
            })
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")
            return
    
    for i, message in enumerate(reversed(st.session_state.chat_history)):
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>{message['question']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 DocMind:</strong><br>{message['answer']}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🧠 DocMind</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Document Intelligence | Powered by DeepSeek, LangChain & ChromaDB</p>', unsafe_allow_html=True)
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    with st.sidebar:
        st.header("📄 Document Upload")
        st.markdown("---")
        
        pdf_docs = st.file_uploader(
            "Upload your PDF documents",
            accept_multiple_files=True,
            type=['pdf']
        )
        
        if st.button("🚀 Process Documents"):
            if not pdf_docs:
                st.warning("Please upload at least one PDF document!")
            else:
                with st.spinner("Processing your documents..."):
                    try:
                        raw_text = get_pdf_text(pdf_docs)
                        
                        if not raw_text.strip():
                            st.error("No text found in the uploaded documents!")
                            return
                        
                        process_start_time = time.time()
                        text_chunks = get_text_chunks(raw_text)
                        PROCESSING_TIME.observe(time.time() - process_start_time)
                        
                        st.success(f"Created {len(text_chunks)} text chunks")
                        vectorstore = get_vectorstore(text_chunks)
                        st.session_state.conversation = get_conversation_chain(vectorstore)
                        
                        st.success("✅ Documents processed successfully! You can now ask questions.")
                        
                    except Exception as e:
                        st.error(f"Error during processing: {str(e)}")
        
        st.markdown("---")
        st.markdown("""
        ### 📊 Features
        - 🔍 Conversational Document Search
        - 🧠 AI-Powered Q&A
        - 🎯 RAG Architecture
        - ⚡ Real-time Responses
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🛠️ Tech Stack
        - **LLM:** DeepSeek (via Ollama)
        - **Framework:** LangChain
        - **Vector DB:** ChromaDB
        - **UI:** Streamlit
        """)
    
    st.markdown("### 💬 Chat with Your Documents")
    
    user_question = st.text_input(
        "Ask a question about your documents:",
        placeholder="e.g., What is the main topic of these documents?",
        key="user_input"
    )
    
    if user_question:
        handle_user_input(user_question)
    
    if st.session_state.conversation is None:
        st.info("""
        👋 **Welcome to DocMind!**
        
        To get started:
        1. Upload your PDF documents using the sidebar
        2. Click "Process Documents" to analyze them
        3. Ask questions about your documents in the chat box above
        
        **Note:** Make sure Ollama is running with the DeepSeek model installed:
        ```bash
        ollama pull deepseek-r1:1.5b
        ollama serve
        ```
        """)

if __name__ == '__main__':
    main()
