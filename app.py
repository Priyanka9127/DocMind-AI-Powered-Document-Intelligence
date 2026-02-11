import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import os

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
    .exam-card {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .exam-card h3 {
        color: #764ba2;
        margin-top: 0;
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
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    """Create ChromaDB vector store with embeddings"""
    # Use a persistent directory for ChromaDB
    persist_directory = "./chroma_db"
    
    # Create embeddings using Ollama
    embeddings = OllamaEmbeddings(
        model="deepseek-r1:1.5b",  # Using DeepSeek model via Ollama
        base_url="http://localhost:11434"
    )
    
    # Create unique collection name based on timestamp
    import time
    collection_name = f"documents_{int(time.time())}"
    
    # Create ChromaDB vector store
    vectorstore = Chroma.from_texts(
        texts=text_chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    return vectorstore


def get_conversation_chain(vectorstore):
    """Create conversational retrieval chain with DeepSeek LLM"""
    # Initialize DeepSeek LLM via Ollama
    llm = Ollama(
        model="deepseek-r1:1.5b",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    
    # Create conversation memory
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )
    
    # Create conversational retrieval chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True
    )
    
    return conversation_chain


def generate_mcq_questions(text_chunks, num_questions=5):
    """Generate Multiple Choice Questions from document chunks"""
    llm = Ollama(
        model="deepseek-r1:1.5b",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    
    context = "\n\n".join(text_chunks[:10])
    
    prompt = f"""Based on the following document content, generate {num_questions} multiple choice questions (MCQs).
    
    Format the output exactly like this using Markdown:
    
    ### Question 1
    [The Question content]
    - A) [Option 1]
    - B) [Option 2]
    - C) [Option 3]
    - D) [Option 4]
    
    **Correct Answer:** [Option] - [Explanation]
    
    ---
    
    [Repeat for all questions]
    
    Document Content:
    {context[:3000]}
    """
    
    response = llm(prompt)
    return clean_llm_response(response)


def generate_essay_questions(text_chunks, num_questions=3):
    """Generate Essay Questions from document chunks"""
    llm = Ollama(
        model="deepseek-r1:1.5b",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    
    context = "\n\n".join(text_chunks[:10])
    
    prompt = f"""Based on the following document content, generate {num_questions} thought-provoking essay questions.
    
    Format the output exactly like this using Markdown:
    
    ### Question 1
    **[Question Title/Topic]**
    > [The detailed question content asking for analysis or explanation]
    
    *Key points to cover in answer: [Brief list of expected points]*
    
    ---
    
    [Repeat for all questions]
    
    Document Content:
    {context[:3000]}
    """
    
    response = llm(prompt)
    return clean_llm_response(response)


def generate_flashcards(text_chunks, num_cards=10):
    """Generate Flashcards from document chunks"""
    llm = Ollama(
        model="deepseek-r1:1.5b",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    
    context = "\n\n".join(text_chunks[:10])
    
    prompt = f"""Based on the following document content, generate {num_cards} flashcards.
    
    Format the output exactly like this using Markdown:
    
    ### Card 1
    **Front:** [Concept or Question]
    **Back:** [Definition or Answer]
    
    ---
    
    [Repeat for all cards]
    
    Document Content:
    {context[:3000]}
    """
    
    response = llm(prompt)
    return clean_llm_response(response)


def handle_user_input(user_question):
    """Process user questions and display responses"""
    if st.session_state.conversation is None:
        st.warning("⚠️ Please upload and process documents first!")
        return
    
    with st.spinner("🤔 Thinking..."):
        try:
            response = st.session_state.conversation({'question': user_question})
            answer = clean_llm_response(response['answer'])
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': answer
            })
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")
            return
    
    # Display chat history (newest first)
    for i, message in enumerate(reversed(st.session_state.chat_history)):
        # User message
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>{message['question']}
        </div>
        """, unsafe_allow_html=True)
        
        # Bot message
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 DocMind:</strong><br>{message['answer']}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🧠 DocMind</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Document Intelligence | Powered by DeepSeek, LangChain & ChromaDB</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "text_chunks" not in st.session_state:
        st.session_state.text_chunks = None
    # Initialize exam session state
    if "exam_mcqs" not in st.session_state:
        st.session_state.exam_mcqs = None
    if "exam_essays" not in st.session_state:
        st.session_state.exam_essays = None
    if "exam_flashcards" not in st.session_state:
        st.session_state.exam_flashcards = None
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📄 Document Upload")
        st.markdown("---")
        
        pdf_docs = st.file_uploader(
            "Upload your PDF documents",
            accept_multiple_files=True,
            type=['pdf'],
            help="Upload one or more PDF files to analyze"
        )
        
        if st.button("🚀 Process Documents"):
            if not pdf_docs:
                st.warning("Please upload at least one PDF document!")
            else:
                with st.spinner("Processing your documents..."):
                    try:
                        # Extract text from PDFs
                        st.info("📖 Extracting text from PDFs...")
                        raw_text = get_pdf_text(pdf_docs)
                        
                        if not raw_text.strip():
                            st.error("No text found in the uploaded documents!")
                            return
                        
                        # Split text into chunks
                        st.info("✂️ Splitting text into chunks...")
                        text_chunks = get_text_chunks(raw_text)
                        st.session_state.text_chunks = text_chunks  # Store for exam generation
                        st.success(f"Created {len(text_chunks)} text chunks")
                        
                        # Create vector store
                        st.info("🔮 Creating vector embeddings with ChromaDB...")
                        vectorstore = get_vectorstore(text_chunks)
                        
                        # Create conversation chain
                        st.info("🔗 Initializing conversation chain...")
                        st.session_state.conversation = get_conversation_chain(vectorstore)
                        
                        st.success("✅ Documents processed successfully! You can now ask questions.")
                        
                    except Exception as e:
                        st.error(f"Error during processing: {str(e)}")
        
        st.markdown("---")
        st.markdown("""
        ### 📊 Features
        - 🔍 Conversational Document Search
        - 🧠 AI-Powered Q&A
        - 📚 Multi-Document Support
        - 🎯 RAG Architecture
        - ⚡ Real-time Responses
        - 📝 Exam Generation (MCQ, Essay, Flashcards)
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🛠️ Tech Stack
        - **LLM:** DeepSeek (via Ollama)
        - **Framework:** LangChain
        - **Vector DB:** ChromaDB
        - **UI:** Streamlit
        """)
    
    # Create tabs for different features
    tab1, tab2 = st.tabs(["💬 Document Chat", "📝 Exam Generation"])
    
    with tab1:
        st.markdown("### 💬 Chat with Your Documents")
        
        user_question = st.text_input(
            "Ask a question about your documents:",
            placeholder="e.g., What is the main topic of these documents?",
            key="user_input"
        )
        
        if user_question:
            handle_user_input(user_question)
        
        # Display instructions if no conversation started
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
    
    with tab2:
        st.markdown("### 📝 AI-Powered Exam Generation")
        
        if "text_chunks" not in st.session_state or st.session_state.text_chunks is None:
            st.warning("⚠️ Please upload and process documents first to generate exams!")
        else:
            st.info("🎓 Generate exams, quizzes, and study materials from your documents")
            
            # Controls Area
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📋 Multiple Choice")
                num_mcq = st.slider("Number of MCQs", 3, 10, 5, key="mcq_slider")
                if st.button("Generate MCQs", key="gen_mcq"):
                    with st.spinner("Generating MCQ questions..."):
                        try:
                            response = generate_mcq_questions(st.session_state.text_chunks, num_mcq)
                            st.session_state.exam_mcqs = response
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col2:
                st.markdown("#### ✍️ Essay Questions")
                num_essay = st.slider("Number of Questions", 2, 5, 3, key="essay_slider")
                if st.button("Generate Essays", key="gen_essay"):
                    with st.spinner("Generating essay questions..."):
                        try:
                            response = generate_essay_questions(st.session_state.text_chunks, num_essay)
                            st.session_state.exam_essays = response
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col3:
                st.markdown("#### 🎴 Flashcards")
                num_cards = st.slider("Number of Cards", 5, 15, 10, key="card_slider")
                if st.button("Generate Flashcards", key="gen_cards"):
                    with st.spinner("Generating flashcards..."):
                        try:
                            response = generate_flashcards(st.session_state.text_chunks, num_cards)
                            st.session_state.exam_flashcards = response
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            st.markdown("---")
            
            # Display Results (Full Width)
            if st.session_state.exam_mcqs:
                with st.expander("📋 Multiple Choice Questions", expanded=True):
                    st.markdown(st.session_state.exam_mcqs)
                    
            if st.session_state.exam_essays:
                with st.expander("✍️ Essay Questions", expanded=True):
                    st.markdown(st.session_state.exam_essays)
                    
            if st.session_state.exam_flashcards:
                with st.expander("🎴 Flashcards", expanded=True):
                    st.markdown(st.session_state.exam_flashcards)


if __name__ == '__main__':
    main()
