# 🚀 DocMind Setup Guide

This guide will help you set up and run DocMind on your local machine.

## Step-by-Step Setup

### 1️⃣ Install Ollama

**Windows:**
1. Download Ollama from https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2️⃣ Install DeepSeek Model

Open a terminal and run:
```bash
ollama pull deepseek-r1:1.5b
```

This will download the DeepSeek model (approximately 900MB).

### 3️⃣ Start Ollama Server

```bash
ollama serve
```

Keep this terminal window open. You should see:
```
Ollama is running on http://localhost:11434
```

### 4️⃣ Install Python Dependencies

Open a **new terminal** window and navigate to the DocMind1 folder:

```bash
cd C:\Users\priya\Desktop\DocMind1
```

Install the required packages:
```bash
pip install -r requirements.txt
```

### 5️⃣ Run DocMind

```bash
streamlit run app.py
```

Your browser should automatically open to `http://localhost:8501`

## 🎯 Quick Test

1. **Upload a PDF**: Use the sidebar to upload a test PDF document
2. **Process**: Click "🚀 Process Documents"
3. **Ask a Question**: Try asking "What is this document about?"

## 🔍 Verify Installation

### Check Ollama is Running
```bash
ollama list
```

You should see `deepseek-r1:1.5b` in the list.

### Test Ollama
```bash
ollama run deepseek-r1:1.5b "Hello, how are you?"
```

You should get a response from the model.

### Check Python Packages
```bash
pip list | grep -E "streamlit|langchain|chromadb"
```

## ⚙️ Alternative Models

If you want to use a different model, you can:

1. **Pull a different model**:
```bash
ollama pull llama2
# or
ollama pull mistral
```

2. **Update app.py**:
Change the model name in two places:
```python
# Line ~87
embeddings = OllamaEmbeddings(
    model="llama2",  # Change here
    base_url="http://localhost:11434"
)

# Line ~101
llm = Ollama(
    model="llama2",  # Change here
    base_url="http://localhost:11434",
    temperature=0.7
)
```

## 🐛 Common Issues

### Issue: "Connection refused" error
**Solution**: Make sure Ollama is running (`ollama serve`)

### Issue: "Model not found"
**Solution**: Pull the model first (`ollama pull deepseek-r1:1.5b`)

### Issue: Streamlit won't start
**Solution**: 
- Check if port 8501 is available
- Try: `streamlit run app.py --server.port 8502`

### Issue: ChromaDB errors
**Solution**: Delete the `chroma_db` folder and reprocess documents

### Issue: Out of memory
**Solution**: 
- Use a smaller model (e.g., `deepseek-r1:1.5b` instead of larger variants)
- Process fewer documents at once
- Reduce chunk size in `app.py`

## 📊 Performance Tips

1. **For faster processing**: Use smaller models
2. **For better accuracy**: Use larger models (e.g., `deepseek-r1:7b`)
3. **For large documents**: Increase chunk overlap
4. **For better retrieval**: Increase the `k` value in retrieval settings

## 🎓 Next Steps

Once everything is running:
- Try uploading different types of PDFs
- Experiment with different questions
- Adjust the parameters for better results
- Add more features (exam generation, summarization, etc.)

## 💡 Tips for Demo/Interview

1. **Prepare sample PDFs**: Have 2-3 interesting PDFs ready
2. **Prepare questions**: Write down good example questions
3. **Explain the architecture**: Use the `image.png` diagram
4. **Highlight features**: 
   - RAG architecture
   - 90% accuracy claim
   - Real-time processing
   - Multi-document support

---

**Need help?** Check the main README.md or the troubleshooting section above.
